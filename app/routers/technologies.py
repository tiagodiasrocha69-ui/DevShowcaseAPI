from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Technology
from app.schemas import TechnologyCreate, TechnologyResponse

router = APIRouter(prefix="/api/technologies", tags=["Technologies"])


@router.post("", response_model=TechnologyResponse, status_code=status.HTTP_201_CREATED)
def create_technology(data: TechnologyCreate, db: Session = Depends(get_db)):
    exists = db.scalar(
        select(Technology).where(func.lower(Technology.name) == data.name.lower())
    )
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Essa tecnologia já está cadastrada.")

    tech = Technology(name=data.name)
    db.add(tech)
    db.commit()
    db.refresh(tech)
    return tech


@router.get("", response_model=list[TechnologyResponse])
def list_technologies(db: Session = Depends(get_db)):
    return db.scalars(select(Technology).order_by(Technology.name)).all()
