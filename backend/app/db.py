import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SqliteRepository:
    _lock = threading.Lock()
    _initialized = False
    _db_path: Optional[Path] = None

    @classmethod
    def initialize(cls, path: str) -> None:
        cls._db_path = Path(path)
        cls._db_path.parent.mkdir(parents=True, exist_ok=True)
        with cls._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    progress INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    config_json TEXT,
                    max_documents INTEGER,
                    result_json TEXT
                )
                """
            )
            columns = {row[1] for row in cursor.execute("PRAGMA table_info(jobs)").fetchall()}
            if "config_json" not in columns:
                cursor.execute("ALTER TABLE jobs ADD COLUMN config_json TEXT")
            if "max_documents" not in columns:
                cursor.execute("ALTER TABLE jobs ADD COLUMN max_documents INTEGER")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS templates (
                    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            template_columns = {row[1] for row in cursor.execute("PRAGMA table_info(templates)").fetchall()}
            if "description" not in template_columns:
                cursor.execute("ALTER TABLE templates ADD COLUMN description TEXT")
            conn.commit()
        cls._initialized = True

    @classmethod
    def _assert_initialized(cls) -> None:
        if cls._db_path is None:
            raise RuntimeError("SQLite repository is not initialized")

    @classmethod
    def _connect(cls) -> sqlite3.Connection:
        cls._assert_initialized()
        conn = sqlite3.connect(str(cls._db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def create_job(cls, job_id: str, status: str = "pending", config: Optional[Dict[str, Any]] = None, max_documents: Optional[int] = None) -> None:
        now = datetime.utcnow().isoformat()
        config_json = json.dumps(config, default=str) if config is not None else None
        with cls._lock, cls._connect() as conn:
            conn.execute(
                "INSERT INTO jobs (job_id, status, progress, created_at, updated_at, config_json, max_documents) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (job_id, status, 0, now, now, config_json, max_documents),
            )
            conn.commit()

    @classmethod
    def update_job_status(cls, job_id: str, status: str, progress: Optional[int] = None) -> None:
        now = datetime.utcnow().isoformat()
        with cls._lock, cls._connect() as conn:
            if progress is None:
                conn.execute(
                    "UPDATE jobs SET status = ?, updated_at = ? WHERE job_id = ?",
                    (status, now, job_id),
                )
            else:
                conn.execute(
                    "UPDATE jobs SET status = ?, progress = ?, updated_at = ? WHERE job_id = ?",
                    (status, progress, now, job_id),
                )
            conn.commit()

    @classmethod
    def store_job_result(cls, job_id: str, result: Dict[str, Any]) -> None:
        now = datetime.utcnow().isoformat()
        payload = json.dumps(result, default=str)
        with cls._lock, cls._connect() as conn:
            conn.execute(
                "UPDATE jobs SET result_json = ?, updated_at = ? WHERE job_id = ?",
                (payload, now, job_id),
            )
            conn.commit()

    @classmethod
    def delete_job(cls, job_id: str) -> None:
        with cls._lock, cls._connect() as conn:
            conn.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
            conn.commit()

    @classmethod
    def get_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        with cls._connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
            if not row:
                return None
            return {
                "jobId": row["job_id"],
                "status": row["status"],
                "progress": row["progress"],
                "createdAt": row["created_at"],
                "updatedAt": row["updated_at"],
                "canRerun": bool(row["config_json"]),
                "result": json.loads(row["result_json"]) if row["result_json"] else None,
            }

    @classmethod
    def list_jobs(cls) -> List[Dict[str, Any]]:
        with cls._connect() as conn:
            rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
            return [
                {
                    "jobId": row["job_id"],
                    "status": row["status"],
                    "progress": row["progress"],
                    "createdAt": row["created_at"],
                    "updatedAt": row["updated_at"],
                    "canRerun": bool(row["config_json"]),
                    "result": json.loads(row["result_json"]) if row["result_json"] else None,
                }
                for row in rows
            ]

    @classmethod
    def get_job_config(cls, job_id: str) -> Optional[Dict[str, Any]]:
        with cls._connect() as conn:
            row = conn.execute("SELECT config_json, max_documents FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
            if not row or not row["config_json"]:
                return None
            return {
                "config": json.loads(row["config_json"]),
                "maxDocuments": row["max_documents"],
            }

    @classmethod
    def create_template(cls, name: str, payload: Dict[str, Any], description: Optional[str] = None) -> int:
        now = datetime.utcnow().isoformat()
        payload_json = json.dumps(payload, default=str)
        with cls._lock, cls._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO templates (name, description, payload_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (name, description, payload_json, now, now),
            )
            conn.commit()
            return cursor.lastrowid

    @classmethod
    def update_template(cls, template_id: int, name: str, payload: Dict[str, Any], description: Optional[str] = None) -> None:
        now = datetime.utcnow().isoformat()
        payload_json = json.dumps(payload, default=str)
        with cls._lock, cls._connect() as conn:
            conn.execute(
                "UPDATE templates SET name = ?, description = ?, payload_json = ?, updated_at = ? WHERE template_id = ?",
                (name, description, payload_json, now, template_id),
            )
            conn.commit()

    @classmethod
    def delete_template(cls, template_id: int) -> None:
        with cls._lock, cls._connect() as conn:
            conn.execute("DELETE FROM templates WHERE template_id = ?", (template_id,))
            conn.commit()

    @classmethod
    def get_template(cls, template_id: int) -> Optional[Dict[str, Any]]:
        with cls._connect() as conn:
            row = conn.execute("SELECT * FROM templates WHERE template_id = ?", (template_id,)).fetchone()
            if not row:
                return None
            return {
                "templateId": row["template_id"],
                "name": row["name"],
                "description": row["description"],
                "payload": json.loads(row["payload_json"]),
                "createdAt": row["created_at"],
                "updatedAt": row["updated_at"],
            }

    @classmethod
    def list_templates(cls) -> List[Dict[str, Any]]:
        with cls._connect() as conn:
            rows = conn.execute("SELECT * FROM templates ORDER BY updated_at DESC").fetchall()
            return [
                {
                    "templateId": row["template_id"],
                    "name": row["name"],
                    "description": row["description"],
                    "payload": json.loads(row["payload_json"]),
                    "createdAt": row["created_at"],
                    "updatedAt": row["updated_at"],
                }
                for row in rows
            ]
