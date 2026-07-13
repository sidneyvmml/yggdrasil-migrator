from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import MongoConnectionInfo


def _path_has_dollar_segment(path: str) -> bool:
    return any(segment.startswith("$") for segment in path.split("."))


class KeycloakConnectionInfo(BaseModel):
    baseUrl: str = Field(..., min_length=8)
    realm: str = Field(..., min_length=1)
    authMode: Literal["client_credentials", "password"] = "client_credentials"
    clientId: str = Field(..., min_length=1)
    clientSecret: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @field_validator("clientSecret")
    @classmethod
    def validate_client_secret(cls, v: Optional[str], info):
        auth_mode = info.data.get("authMode", "client_credentials")
        if auth_mode == "client_credentials" and not (v or "").strip():
            raise ValueError("clientSecret is required when authMode is 'client_credentials'")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str], info):
        auth_mode = info.data.get("authMode", "client_credentials")
        if auth_mode == "password" and not (v or "").strip():
            raise ValueError("username is required when authMode is 'password'")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str], info):
        auth_mode = info.data.get("authMode", "client_credentials")
        if auth_mode == "password" and not (v or "").strip():
            raise ValueError("password is required when authMode is 'password'")
        return v


class KeycloakValidateRequest(KeycloakConnectionInfo):
    pass


class KeycloakUsersRequest(KeycloakConnectionInfo):
    first: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)
    filterMode: Literal["none", "field", "fieldValue"] = "none"
    filterField: Optional[str] = None
    filterOperator: Literal["eq", "ne", "contains", "gt", "gte", "lt", "lte", "null", "notNull"] = "eq"
    filterValue: Optional[Any] = None

    @model_validator(mode="after")
    def validate_filter_fields(self):
        if self.filterMode in {"field", "fieldValue"} and not (self.filterField or "").strip():
            raise ValueError("filterField is required when filterMode is 'field' or 'fieldValue'")

        if self.filterMode == "fieldValue":
            if self.filterOperator in {"null", "notNull"}:
                return self

            if self.filterValue is None:
                raise ValueError("filterValue is required for the selected filterOperator")

            if isinstance(self.filterValue, str) and not self.filterValue.strip():
                raise ValueError("filterValue cannot be empty for the selected filterOperator")

        return self


class KeycloakMigrationConfig(BaseModel):
    migrationType: Literal["keycloak"] = "keycloak"
    migrationName: str = Field(..., min_length=1)
    source: KeycloakConnectionInfo
    target: KeycloakConnectionInfo
    usernameSourceField: str = Field(default="username", min_length=1)
    fieldMapping: Dict[str, str] = {}

    @field_validator("usernameSourceField")
    @classmethod
    def validate_username_source_field(cls, v: str) -> str:
        if _path_has_dollar_segment(v):
            raise ValueError("usernameSourceField cannot contain segments starting with '$'")
        return v

    @field_validator("fieldMapping")
    @classmethod
    def validate_field_mapping(cls, v: Dict[str, str]) -> Dict[str, str]:
        for source_path, target_path in v.items():
            if _path_has_dollar_segment(source_path) or _path_has_dollar_segment(target_path):
                raise ValueError("fieldMapping paths cannot contain segments starting with '$'")
        return v


class MongoToKeycloakMigrationConfig(BaseModel):
    migrationType: Literal["mongo_to_keycloak"] = "mongo_to_keycloak"
    migrationName: str = Field(..., min_length=1)
    source: MongoConnectionInfo
    target: KeycloakConnectionInfo
    sourceMatchField: str = Field(..., min_length=1)
    targetMatchField: str = Field(default="username", min_length=1)
    fieldMapping: Dict[str, str] = {}

    @field_validator("sourceMatchField", "targetMatchField")
    @classmethod
    def validate_match_field(cls, v: str) -> str:
        if _path_has_dollar_segment(v):
            raise ValueError("match fields cannot contain segments starting with '$'")
        return v

    @field_validator("fieldMapping")
    @classmethod
    def validate_field_mapping(cls, v: Dict[str, str]) -> Dict[str, str]:
        for source_path, target_path in v.items():
            if _path_has_dollar_segment(source_path) or _path_has_dollar_segment(target_path):
                raise ValueError("fieldMapping paths cannot contain segments starting with '$'")
        return v


class KeycloakPreviewRequest(BaseModel):
    config: KeycloakMigrationConfig
    limit: int = Field(default=10, ge=1, le=50)


class KeycloakExecuteRequest(BaseModel):
    config: KeycloakMigrationConfig | MongoToKeycloakMigrationConfig
    maxDocuments: Optional[int] = Field(default=None, ge=1)


class KeycloakPreviewResponse(BaseModel):
    items: List[Dict[str, Any]]
