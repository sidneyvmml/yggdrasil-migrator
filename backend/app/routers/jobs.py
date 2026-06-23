from fastapi import APIRouter, HTTPException

from app.db import SqliteRepository
from app.workers.tasks import execute_migration_job

router = APIRouter()


def _normalize_filter_rules(config: dict) -> dict:
    rules = config.get("filterRules")
    if not isinstance(rules, list):
        return config

    normalized_rules = []
    for rule in rules:
        if not isinstance(rule, dict):
            normalized_rules.append(rule)
            continue

        if rule.get("op") == "truthy":
            normalized_rule = dict(rule)
            normalized_rule["op"] = "eq"
            normalized_rule["value"] = True
            normalized_rules.append(normalized_rule)
            continue

        normalized_rules.append(rule)

    normalized = dict(config)
    normalized["filterRules"] = normalized_rules
    return normalized


@router.get("/", response_model=list)
def list_jobs():
    return SqliteRepository.list_jobs()


@router.get("/{job_id}")
def get_job(job_id: str):
    result = SqliteRepository.get_job(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.post("/{job_id}/rerun")
def rerun_job(job_id: str):
    stored = SqliteRepository.get_job_config(job_id)
    if stored is None:
        raise HTTPException(status_code=400, detail="This job cannot be re-run because its config was not stored.")

    try:
        config_payload = _normalize_filter_rules(stored["config"])
        job = execute_migration_job.apply_async(args=[config_payload, stored["maxDocuments"]])
        SqliteRepository.create_job(job.id, status="pending", config=config_payload, max_documents=stored["maxDocuments"])
        return {"jobId": job.id, "status": "pending"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Failed to enqueue rerun job: {exc}") from exc


@router.delete("/{job_id}")
def delete_job(job_id: str):
    existing = SqliteRepository.get_job(job_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Job not found")

    SqliteRepository.delete_job(job_id)
    return {"deleted": True, "jobId": job_id}
