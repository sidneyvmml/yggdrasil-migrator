import asyncio
from urllib.parse import quote, urlsplit, urlunsplit


class PostgresExplorationService:
    @staticmethod
    def _with_database(connection_string: str, database: str) -> str:
        parts = urlsplit(connection_string)
        db_path = f"/{quote(database.strip())}"
        return urlunsplit((parts.scheme, parts.netloc, db_path, parts.query, parts.fragment))

    @staticmethod
    async def validate_connection(connection_string: str, timeout_seconds: int = 5) -> bool:
        return await asyncio.to_thread(
            PostgresExplorationService._validate_connection_sync,
            connection_string,
            timeout_seconds,
        )

    @staticmethod
    async def list_databases(connection_string: str, timeout_seconds: int = 5) -> list[str]:
        return await asyncio.to_thread(
            PostgresExplorationService._list_databases_sync,
            connection_string,
            timeout_seconds,
        )

    @staticmethod
    async def list_schemas(connection_string: str, database: str, timeout_seconds: int = 5) -> list[str]:
        return await asyncio.to_thread(
            PostgresExplorationService._list_schemas_sync,
            connection_string,
            database,
            timeout_seconds,
        )

    @staticmethod
    async def list_tables(
        connection_string: str,
        database: str,
        schema: str | None = None,
        timeout_seconds: int = 5,
    ) -> list[str]:
        return await asyncio.to_thread(
            PostgresExplorationService._list_tables_sync,
            connection_string,
            database,
            schema,
            timeout_seconds,
        )

    @staticmethod
    def _validate_connection_sync(connection_string: str, timeout_seconds: int) -> bool:
        try:
            import psycopg
        except Exception as exc:  # pragma: no cover - depends on runtime deps
            raise RuntimeError(
                "PostgreSQL driver not installed. Add dependency 'psycopg[binary]' and reinstall project dependencies."
            ) from exc

        with psycopg.connect(connection_string, connect_timeout=timeout_seconds) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

        return True

    @staticmethod
    def _list_databases_sync(connection_string: str, timeout_seconds: int) -> list[str]:
        try:
            import psycopg
        except Exception as exc:  # pragma: no cover - depends on runtime deps
            raise RuntimeError(
                "PostgreSQL driver not installed. Add dependency 'psycopg[binary]' and reinstall project dependencies."
            ) from exc

        with psycopg.connect(connection_string, connect_timeout=timeout_seconds) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT datname
                    FROM pg_database
                    WHERE datistemplate = false
                    ORDER BY datname
                    """
                )
                return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def _list_schemas_sync(connection_string: str, database: str, timeout_seconds: int) -> list[str]:
        try:
            import psycopg
        except Exception as exc:  # pragma: no cover - depends on runtime deps
            raise RuntimeError(
                "PostgreSQL driver not installed. Add dependency 'psycopg[binary]' and reinstall project dependencies."
            ) from exc

        scoped_connection_string = PostgresExplorationService._with_database(connection_string, database)
        with psycopg.connect(scoped_connection_string, connect_timeout=timeout_seconds) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT schema_name
                    FROM information_schema.schemata
                    WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
                      AND schema_name NOT LIKE 'pg_toast%'
                    ORDER BY schema_name
                    """
                )
                return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def _list_tables_sync(
        connection_string: str,
        database: str,
        schema: str | None,
        timeout_seconds: int,
    ) -> list[str]:
        try:
            import psycopg
        except Exception as exc:  # pragma: no cover - depends on runtime deps
            raise RuntimeError(
                "PostgreSQL driver not installed. Add dependency 'psycopg[binary]' and reinstall project dependencies."
            ) from exc

        scoped_connection_string = PostgresExplorationService._with_database(connection_string, database)
        with psycopg.connect(scoped_connection_string, connect_timeout=timeout_seconds) as conn:
            with conn.cursor() as cursor:
                if schema:
                    cursor.execute(
                        """
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_type = 'BASE TABLE'
                          AND table_schema = %s
                        ORDER BY table_name
                        """,
                        (schema,)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT table_schema, table_name
                        FROM information_schema.tables
                        WHERE table_type = 'BASE TABLE'
                          AND table_schema NOT IN ('information_schema', 'pg_catalog')
                          AND table_schema NOT LIKE 'pg_toast%'
                        ORDER BY table_schema, table_name
                        """
                    )
                    return [f"{row[0]}.{row[1]}" for row in cursor.fetchall()]

                return [row[0] for row in cursor.fetchall()]
