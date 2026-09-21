from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Profile
from app.schemas import ProfileCreate, ProfileResponse

router = APIRouter(prefix="/api/profiles", tags=["Profiles"])


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(data: ProfileCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(Profile).where(Profile.email == data.email))
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um perfil com esse e-mail.")

    profile = Profile(**data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(Profile, profile_id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Perfil não encontrado.")
    return profile
