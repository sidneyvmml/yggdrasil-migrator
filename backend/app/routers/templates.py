from fastapi import APIRouter, HTTPException

from app.db import SqliteRepository
from app.schemas.common import TemplateCreateRequest, TemplateUpdateRequest

router = APIRouter()


@router.post("/", status_code=201)
def create_template(payload: TemplateCreateRequest):
    template_id = SqliteRepository.create_template(
        payload.name,
        payload.payload.model_dump(),
        payload.description,
    )
    return {"templateId": template_id}


@router.get("/")
def list_templates():
    return SqliteRepository.list_templates()


@router.get("/{template_id}")
def get_template(template_id: int):
    template = SqliteRepository.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{template_id}")
def update_template(template_id: int, payload: TemplateUpdateRequest):
    template = SqliteRepository.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    SqliteRepository.update_template(
        template_id,
        payload.name,
        payload.payload.model_dump(),
        payload.description,
    )
    return {"templateId": template_id}


@router.delete("/{template_id}", status_code=204)
def delete_template(template_id: int):
    template = SqliteRepository.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    SqliteRepository.delete_template(template_id)
