from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Asset
from app.schemas.asset import AssetCreate

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("")
def list_assets(db: Session = Depends(get_db)) -> list[dict]:
    return [{column.name: getattr(row, column.name) for column in Asset.__table__.columns} for row in db.scalars(select(Asset).order_by(Asset.hostname))]


@router.post("", status_code=201)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)) -> dict:
    if db.scalar(select(Asset).where(Asset.hostname == payload.hostname)):
        raise HTTPException(status_code=409, detail="An asset with this hostname already exists.")
    row = Asset(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {column.name: getattr(row, column.name) for column in Asset.__table__.columns}
