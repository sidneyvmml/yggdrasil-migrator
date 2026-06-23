from copy import deepcopy
import json
from typing import Any, Dict, Iterable, List, Optional

from bson import ObjectId
from bson.json_util import loads as bson_loads
from motor.motor_asyncio import AsyncIOMotorClient

from app.schemas.common import FilterRule, FlattenConfigItem, LookupConfig, MigrationConfig


class MigrationService:
    def __init__(
        self,
        source_client: AsyncIOMotorClient,
        target_client: AsyncIOMotorClient,
        source_db: str,
        source_collection: str,
        target_db: str,
        target_collection: str,
    ):
        self.source_client = source_client
        self.target_client = target_client
        self.source = source_client[source_db][source_collection]
        self.target = target_client[target_db][target_collection]

    @staticmethod
    def apply_field_mapping(document: Dict[str, Any], field_mapping: Dict[str, str]) -> Dict[str, Any]:
        transformed: Dict[str, Any] = {}
        for src, dst in field_mapping.items():
            value = MigrationService.read_value_by_path(document, src)
            if value is not None:
                MigrationService.write_value_by_path(transformed, dst, value)
        return transformed

    @staticmethod
    def read_value_by_path(document: Dict[str, Any], path: str) -> Any:
        current: Any = document
        for segment in path.split("."):
            if not isinstance(current, dict) or segment not in current:
                return None
            current = current[segment]
        return current

    @staticmethod
    def write_value_by_path(target: Dict[str, Any], path: str, value: Any) -> None:
        segments = path.split(".")
        cursor = target
        for idx, segment in enumerate(segments):
            is_last = idx == len(segments) - 1
            if is_last:
                cursor[segment] = value
                return
            if segment not in cursor or not isinstance(cursor[segment], dict):
                cursor[segment] = {}
            cursor = cursor[segment]

    @staticmethod
    def apply_concat_rules(source_document: Dict[str, Any], target_document: Dict[str, Any], concat_rules: List[Any]) -> None:
        for rule in concat_rules:
            values: List[str] = []
            for source_field in rule.sourceFields:
                value = MigrationService.read_value_by_path(source_document, source_field)
                if value is None:
                    continue
                values.append(str(value))

            combined_value = rule.separator.join(values)
            MigrationService.write_value_by_path(target_document, rule.targetField, combined_value)

    @staticmethod
    def apply_dbref_rules(target_document: Dict[str, Any], dbref_rules: List[Any]) -> None:
        for rule in dbref_rules:
            value = MigrationService.read_value_by_path(target_document, rule.targetField)
            if value is None:
                continue

            MigrationService.write_value_by_path(
                target_document,
                rule.targetField,
                {
                    "$id": value,
                    "$ref": rule.fromCollection,
                    "$field": rule.foreignField,
                },
            )

    @staticmethod
    async def apply_lookup(document: Dict[str, Any], lookup: LookupConfig, client: AsyncIOMotorClient, database: str) -> Any:
        foreign_collection = client[database][lookup.fromCollection]
        local_value = document.get(lookup.localField)
        if local_value is None:
            return [] if lookup.isArray else None

        if isinstance(local_value, list):
            foreign_cursor = foreign_collection.find({lookup.foreignField: {"$in": local_value}})
            return [item async for item in foreign_cursor]

        return await foreign_collection.find_one({lookup.foreignField: local_value})

    @staticmethod
    def apply_flatten(items: List[Dict[str, Any]], flatten_rules: List[FlattenConfigItem]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for item in items:
            current_items = [item]
            for rule in flatten_rules:
                next_items: List[Dict[str, Any]] = []
                for current in current_items:
                    value = MigrationService.read_value_by_path(current, rule.field)
                    if rule.mode == "explode" and isinstance(value, list):
                        if not value:
                            next_items.append(current)
                            continue
                        for element in value:
                            cloned = deepcopy(current)
                            MigrationService.write_value_by_path(cloned, rule.field, element)
                            next_items.append(cloned)
                    else:
                        next_items.append(current)
                current_items = next_items
            results.extend(current_items)
        return results

    @staticmethod
    def apply_filters(items: List[Dict[str, Any]], filter_rules: List[FilterRule]) -> List[Dict[str, Any]]:
        if not filter_rules:
            return items

        def _is_truthy(value: Any) -> bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return value != 0
            if isinstance(value, str):
                return value.strip().lower() in {"true", "1", "yes", "y", "on"}
            return bool(value)

        filtered: List[Dict[str, Any]] = []
        for item in items:
            include = True
            for rule in filter_rules:
                value = MigrationService.read_value_by_path(item, rule.field)
                if rule.op == "eq" and value != rule.value:
                    include = False
                    break
                if rule.op == "truthy" and not _is_truthy(value):
                    include = False
                    break
            if include:
                filtered.append(item)
        return filtered

    @staticmethod
    def _is_empty_value(value: Any) -> bool:
        return value is None or value == "" or value == [] or value == {}

    @staticmethod
    def _normalize_manual_value(value: Any) -> Any:
        if not isinstance(value, (dict, list)):
            return value

        try:
            # Convert Mongo Extended JSON literals (e.g. $binary, $oid) into BSON-native values.
            return bson_loads(json.dumps(value))
        except Exception:
            return value

    @staticmethod
    def _merge_fill_missing(target: Dict[str, Any], incoming: Dict[str, Any]) -> None:
        for key, value in incoming.items():
            if key not in target:
                target[key] = deepcopy(value)
                continue

            current_value = target[key]
            if isinstance(current_value, dict) and isinstance(value, dict):
                MigrationService._merge_fill_missing(current_value, value)
                continue

            if MigrationService._is_empty_value(current_value) and not MigrationService._is_empty_value(value):
                target[key] = deepcopy(value)

    @staticmethod
    def _wrap_stage_error(stage: str, exc: Exception) -> Exception:
        message = str(exc)
        if "authentication failed" in message.lower() or "authenticationfailed" in message.lower():
            return Exception(f"MongoDB authentication failed while {stage}. Original error: {message}")
        return Exception(f"MongoDB error while {stage}. Original error: {message}")

    @staticmethod
    def merge_documents_by_field(items: List[Dict[str, Any]], merge_field: str) -> List[Dict[str, Any]]:
        if not merge_field:
            return items

        merged_by_key: Dict[str, Dict[str, Any]] = {}
        merged_items: List[Dict[str, Any]] = []

        for item in items:
            merge_value = MigrationService.read_value_by_path(item, merge_field)
            if merge_value is None or isinstance(merge_value, (dict, list)):
                merged_items.append(item)
                continue

            key = str(merge_value)
            existing = merged_by_key.get(key)
            if existing is None:
                cloned = deepcopy(item)
                merged_by_key[key] = cloned
                merged_items.append(cloned)
                continue

            MigrationService._merge_fill_missing(existing, item)

        return merged_items

    async def preview(self, config: MigrationConfig, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = self.source.find({}, limit=limit)
        documents = [doc async for doc in cursor]
        transformed = []

        for document in documents:
            expanded_documents = self.apply_flatten([document], config.flattenConfig)
            expanded_documents = self.apply_filters(expanded_documents, config.filterRules)

            for expanded_document in expanded_documents:
                mapped = self.apply_field_mapping(expanded_document, config.fieldMapping)
                self.apply_concat_rules(expanded_document, mapped, config.concatRules)
                self.apply_dbref_rules(mapped, config.dbRefRules)
                for manual_target, manual_value in config.manualMapping.items():
                    self.write_value_by_path(mapped, manual_target, self._normalize_manual_value(manual_value))
                for lookup in config.lookups:
                    mapped[lookup.asField] = await self.apply_lookup(mapped, lookup, self.source_client, config.source.database)
                transformed.append(mapped)

        if config.mergeByField:
            transformed = self.merge_documents_by_field(transformed, config.mergeByField)

        return transformed[:limit]

    async def run_batch(
        self,
        config: MigrationConfig,
        batch_size: int = 100,
        max_documents: Optional[int] = None,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        try:
            total_documents = await self.source.estimated_document_count()
            if max_documents is not None:
                total_documents = min(total_documents, max_documents)
        except Exception as exc:
            raise self._wrap_stage_error("counting source documents", exc) from exc

        source_cursor = self.source.find({})
        processed = 0
        inserted = 0
        skipped = 0
        merged = 0
        errors: List[Dict[str, Any]] = []
        batch: List[Dict[str, Any]] = []
        merge_by_field = (config.mergeByField or "").strip()

        try:
            async for source_doc in source_cursor:
                if max_documents is not None and processed >= max_documents:
                    break

                processed += 1
                expanded_sources = self.apply_flatten([source_doc], config.flattenConfig)
                expanded_sources = self.apply_filters(expanded_sources, config.filterRules)

                for expanded_source in expanded_sources:
                    mapped = self.apply_field_mapping(expanded_source, config.fieldMapping)
                    self.apply_concat_rules(expanded_source, mapped, config.concatRules)
                    self.apply_dbref_rules(mapped, config.dbRefRules)
                    for manual_target, manual_value in config.manualMapping.items():
                        self.write_value_by_path(mapped, manual_target, self._normalize_manual_value(manual_value))

                    for lookup in config.lookups:
                        mapped[lookup.asField] = await self.apply_lookup(mapped, lookup, self.source_client, config.source.database)
                    item = mapped
                    if not item.get("_id"):
                        item["_id"] = ObjectId()
                    batch.append(item)

                if len(batch) >= batch_size:
                    if merge_by_field:
                        inserted_batch, merged_batch, skipped_batch, errors_batch = await self._merge_batch_by_field(batch, merge_by_field)
                    else:
                        inserted_batch, merged_batch, skipped_batch, errors_batch = await self._insert_batch(batch)
                    inserted += inserted_batch
                    merged += merged_batch
                    skipped += skipped_batch
                    errors.extend(errors_batch)
                    batch = []
                    if progress_callback and total_documents > 0:
                        progress_callback(min(99, int(processed / total_documents * 100)))
        except Exception as exc:
            raise self._wrap_stage_error("reading from the source MongoDB", exc) from exc

        if batch:
            try:
                if merge_by_field:
                    inserted_batch, merged_batch, skipped_batch, errors_batch = await self._merge_batch_by_field(batch, merge_by_field)
                else:
                    inserted_batch, merged_batch, skipped_batch, errors_batch = await self._insert_batch(batch)
            except Exception as exc:
                raise self._wrap_stage_error("writing to the target MongoDB", exc) from exc
            inserted += inserted_batch
            merged += merged_batch
            skipped += skipped_batch
            errors.extend(errors_batch)
            if progress_callback and total_documents > 0:
                progress_callback(min(99, int(processed / total_documents * 100)))

        return {
            "processed": processed,
            "inserted": inserted,
            "merged": merged,
            "skipped": skipped,
            "errors": errors,
        }

    async def _insert_batch(self, documents: List[Dict[str, Any]]) -> tuple[int, int, int, List[Dict[str, Any]]]:
        inserted = 0
        merged = 0
        skipped = 0
        errors: List[Dict[str, Any]] = []

        for document in documents:
            try:
                await self.target.insert_one(document)
                inserted += 1
            except Exception as exc:
                reason = str(exc)
                if "duplicate key" in reason.lower() or "E11000" in reason:
                    skipped += 1
                else:
                    raise self._wrap_stage_error("writing to the target MongoDB", exc) from exc
        return inserted, merged, skipped, errors

    async def _merge_batch_by_field(
        self,
        documents: List[Dict[str, Any]],
        merge_field: str,
    ) -> tuple[int, int, int, List[Dict[str, Any]]]:
        inserted = 0
        merged = 0
        skipped = 0
        errors: List[Dict[str, Any]] = []

        for document in documents:
            try:
                merge_value = self.read_value_by_path(document, merge_field)
                if merge_value is None or isinstance(merge_value, (dict, list)):
                    await self.target.insert_one(document)
                    inserted += 1
                    continue

                existing = await self.target.find_one({merge_field: merge_value})
                if existing is None:
                    await self.target.insert_one(document)
                    inserted += 1
                    continue

                merged_doc = deepcopy(existing)
                self._merge_fill_missing(merged_doc, document)
                await self.target.replace_one({"_id": existing["_id"]}, merged_doc)
                merged += 1
            except Exception as exc:
                reason = str(exc)
                if "duplicate key" in reason.lower() or "E11000" in reason:
                    skipped += 1
                else:
                    raise self._wrap_stage_error("writing to the target MongoDB", exc) from exc

        return inserted, merged, skipped, errors
