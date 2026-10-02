import csv
import io
import json
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import Boolean, Float, Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ADIssue, Asset, Backup, Patch, VM, Vulnerability

router = APIRouter(prefix="/imports", tags=["imports"])

ENTITY_MODELS = {
    "assets": Asset,
    "patches": Patch,
    "vulnerabilities": Vulnerability,
    "ad_issues": ADIssue,
    "vms": VM,
    "backups": Backup,
}
ALIASES = {
    "hostname": "hostname",
    "server": "hostname",
    "cve": "cve_id",
    "cve id": "cve_id",
    "kb": "kb_number",
    "kb number": "kb_number",
    "vm": "vm_name",
    "system": "protected_system",
    "status": "status",
}
TRUE_VALUES = {"true", "1", "yes", "y"}
FALSE_VALUES = {"false", "0", "no", "n"}


@router.post("")
async def import_file(
    file: UploadFile = File(...),
    entity: str = Query(..., description="One of assets, patches, vulnerabilities, ad_issues, vms, backups"),
    db: Session = Depends(get_db),
) -> dict:
    model = ENTITY_MODELS.get(entity)
    if model is None:
        raise HTTPException(status_code=422, detail=f"Unsupported entity '{entity}'.")
    if not file.filename or not file.filename.lower().endswith((".csv", ".json")):
        raise HTTPException(status_code=415, detail="Upload a .csv or .json file.")
    raw = await file.read(5 * 1024 * 1024 + 1)
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Import files must be 5 MB or smaller.")
    try:
        text = raw.decode("utf-8-sig")
        if file.filename.lower().endswith(".json"):
            parsed = json.loads(text)
            records = parsed if isinstance(parsed, list) else parsed.get("records") if isinstance(parsed, dict) else None
            if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
                raise ValueError("JSON must be an array of objects or an object with a records array.")
        else:
            records = list(csv.DictReader(io.StringIO(text)))
            if not records or not csv.DictReader(io.StringIO(text)).fieldnames:
                raise ValueError("CSV must include a header and at least one record.")
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse import: {exc}") from exc

    if not records:
        raise HTTPException(status_code=422, detail="The import must contain at least one record.")
    columns = {column.name: column for column in model.__table__.columns if column.name != "id"}
    normalized = []
    for line, record in enumerate(records, start=2):
        row = {}
        for raw_key, raw_value in record.items():
            key = (raw_key or "").strip().lower().replace("-", "_").replace(" ", "_")
            key = ALIASES.get(key.replace("_", " "), key)
            if key not in columns:
                continue
            value = raw_value.strip() if isinstance(raw_value, str) else raw_value
            column = columns[key]
            if value in (None, "") and isinstance(column.type, (Boolean, Integer, Float)):
                continue
            if isinstance(column.type, Boolean):
                if str(value).lower() in TRUE_VALUES:
                    value = True
                elif str(value).lower() in FALSE_VALUES:
                    value = False
                else:
                    raise HTTPException(status_code=422, detail=f"Invalid boolean for '{key}' on row {line}.")
            elif isinstance(column.type, (Integer, Float)) and value not in (None, ""):
                try:
                    value = int(value) if isinstance(column.type, Integer) else float(value)
                except (TypeError, ValueError) as exc:
                    raise HTTPException(status_code=422, detail=f"Invalid number for '{key}' on row {line}.") from exc
            row[key] = value
        if not row:
            raise HTTPException(status_code=422, detail=f"No recognized fields on row {line}.")
        normalized.append(row)

    required_by_model = {
        Asset: "hostname", Patch: "title", Vulnerability: "cve_id", ADIssue: "issue_type",
        VM: "vm_name", Backup: "protected_system",
    }
    required = required_by_model[model]
    if any(not row.get(required) for row in normalized):
        raise HTTPException(status_code=422, detail=f"Every row must include '{required}'.")
    db.add_all(model(**row) for row in normalized)
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail="Import failed validation; no records were imported.") from exc
    return {"entity": entity, "imported": len(normalized), "filename": file.filename}
