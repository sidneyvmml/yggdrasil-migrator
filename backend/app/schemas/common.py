from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    pass


def _path_has_dollar_segment(path: str) -> bool:
    return any(segment.startswith("$") for segment in path.split("."))


class MongoConnectionInfo(BaseModel):
    connectionString: str = Field(..., min_length=10)
    database: str = Field(..., min_length=1)
    collection: str = Field(..., min_length=1)
    authSource: Optional[str] = None


class MongoConnectionRequest(BaseModel):
    connectionString: str = Field(..., min_length=10)
    authSource: Optional[str] = None


class MongoDatabaseRequest(MongoConnectionRequest):
    database: str = Field(..., min_length=1)


class MongoCollectionRequest(MongoDatabaseRequest):
    collection: str = Field(..., min_length=1)


class MongoDocumentRequest(MongoCollectionRequest):
    documentId: str = Field(..., min_length=1)


class TemplateConnectionInfo(BaseModel):
    database: str = Field(..., min_length=1)
    collection: str = Field(..., min_length=1)


class LookupConfig(BaseModel):
    fromCollection: str = Field(..., min_length=1)
    localField: str = Field(..., min_length=1)
    foreignField: str = Field(..., min_length=1)
    asField: str = Field(..., alias="as")
    isArray: bool = False

    model_config = ConfigDict(populate_by_name=True)


class FlattenConfigItem(BaseModel):
    field: str = Field(..., min_length=1)
    mode: str

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        if v not in ("preserve", "explode"):
            raise ValueError("mode must be 'preserve' or 'explode'")
        return v


class FilterRule(BaseModel):
    field: str = Field(..., min_length=1)
    op: Literal["eq", "truthy"] = "eq"
    value: Optional[Any] = None

    @field_validator("field")
    @classmethod
    def validate_field(cls, v: str) -> str:
        if _path_has_dollar_segment(v):
            raise ValueError("filter field cannot contain segments starting with '$'")
        return v

    @model_validator(mode="after")
    def validate_value_for_op(self):
        if self.op == "eq" and self.value is None:
            raise ValueError("value is required when filter op is 'eq'")
        return self


class ConcatRule(BaseModel):
    sourceFields: List[str] = Field(..., min_length=2, max_length=2)
    targetField: str = Field(..., min_length=1)
    separator: str = ""

    @field_validator("sourceFields")
    @classmethod
    def validate_source_fields(cls, v: List[str]) -> List[str]:
        if len(v) != 2:
            raise ValueError("sourceFields must contain exactly two fields")
        for path in v:
            if not path or _path_has_dollar_segment(path):
                raise ValueError("sourceFields paths cannot be empty or contain segments starting with '$'")
        return v

    @field_validator("targetField")
    @classmethod
    def validate_target_field(cls, v: str) -> str:
        if _path_has_dollar_segment(v):
            raise ValueError("targetField cannot contain segments starting with '$'")
        return v


class DbRefRule(BaseModel):
    targetField: str = Field(..., min_length=1)
    fromCollection: str = Field(..., min_length=1)
    foreignField: str = Field(default="_id", min_length=1)

    @field_validator("targetField")
    @classmethod
    def validate_target_field(cls, v: str) -> str:
        if _path_has_dollar_segment(v):
            raise ValueError("targetField cannot contain segments starting with '$'")
        return v

    @field_validator("foreignField")
    @classmethod
    def validate_foreign_field(cls, v: str) -> str:
        if _path_has_dollar_segment(v):
            raise ValueError("foreignField cannot contain segments starting with '$'")
        return v


class MigrationConfig(BaseModel):
    migrationName: str = Field(..., min_length=1)
    source: MongoConnectionInfo
    target: MongoConnectionInfo
    sourceBaseDocumentId: Optional[str] = None
    fieldMapping: Dict[str, str]
    manualMapping: Dict[str, Any] = {}
    concatRules: List[ConcatRule] = []
    dbRefRules: List[DbRefRule] = []
    mergeByField: Optional[str] = None
    lookups: List[LookupConfig] = []
    flattenConfig: List[FlattenConfigItem] = []
    filterRules: List[FilterRule] = []

    @field_validator("fieldMapping")
    @classmethod
    def mapping_not_empty(cls, v: Dict[str, str]) -> Dict[str, str]:
        for source_path, target_path in v.items():
            if _path_has_dollar_segment(source_path) or _path_has_dollar_segment(target_path):
                raise ValueError("fieldMapping paths cannot contain segments starting with '$'")
        return v

    @field_validator("manualMapping")
    @classmethod
    def manual_mapping_valid_keys(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        for key in v.keys():
            if not key or not isinstance(key, str):
                raise ValueError("manualMapping keys must be non-empty strings")
            if _path_has_dollar_segment(key):
                raise ValueError("manualMapping keys cannot contain segments starting with '$'")
        return v

    @field_validator("mergeByField")
    @classmethod
    def validate_merge_field(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("mergeByField cannot be empty")
        if _path_has_dollar_segment(v):
            raise ValueError("mergeByField cannot contain segments starting with '$'")
        return v.strip()

    @field_validator("flattenConfig")
    @classmethod
    def ensure_some_mapping(cls, v: List[FlattenConfigItem], info):
        field_mapping = info.data.get("fieldMapping") or {}
        manual_mapping = info.data.get("manualMapping") or {}
        concat_rules = info.data.get("concatRules") or []
        if not field_mapping and not manual_mapping and not concat_rules:
            raise ValueError("At least one field mapping, manual mapping, or concat rule is required")
        return v


class TemplatePayload(BaseModel):
    migrationName: str = Field(..., min_length=1)
    source: TemplateConnectionInfo
    target: TemplateConnectionInfo
    sourceBaseDocumentId: Optional[str] = None
    fieldMapping: Dict[str, str]
    manualMapping: Dict[str, Any] = {}
    concatRules: List[ConcatRule] = []
    dbRefRules: List[DbRefRule] = []
    mergeByField: Optional[str] = None
    lookups: List[LookupConfig] = []
    flattenConfig: List[FlattenConfigItem] = []
    filterRules: List[FilterRule] = []

    @field_validator("fieldMapping")
    @classmethod
    def mapping_not_empty(cls, v: Dict[str, str]) -> Dict[str, str]:
        for source_path, target_path in v.items():
            if _path_has_dollar_segment(source_path) or _path_has_dollar_segment(target_path):
                raise ValueError("fieldMapping paths cannot contain segments starting with '$'")
        return v

    @field_validator("manualMapping")
    @classmethod
    def manual_mapping_valid_keys(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        for key in v.keys():
            if not key or not isinstance(key, str):
                raise ValueError("manualMapping keys must be non-empty strings")
            if _path_has_dollar_segment(key):
                raise ValueError("manualMapping keys cannot contain segments starting with '$'")
        return v

    @field_validator("mergeByField")
    @classmethod
    def validate_merge_field(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("mergeByField cannot be empty")
        if _path_has_dollar_segment(v):
            raise ValueError("mergeByField cannot contain segments starting with '$'")
        return v.strip()


class TemplateCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    payload: TemplatePayload


class TemplateUpdateRequest(TemplateCreateRequest):
    pass


class JobCreateRequest(BaseModel):
    config: MigrationConfig
    maxDocuments: Optional[int] = Field(default=None, ge=1)


class JobStatusResponse(BaseModel):
    jobId: str
    status: str
    progress: int
    createdAt: str
    updatedAt: str
    result: Optional[Dict[str, Any]] = None


class PreviewResponse(BaseModel):
    items: List[Dict[str, Any]]
