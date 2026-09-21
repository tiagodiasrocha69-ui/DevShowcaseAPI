from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Profile, Project, Technology
from app.schemas import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    profile = db.get(Profile, data.profile_id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Perfil não encontrado.")

    ids = set(data.technology_ids)
    technologies = []
    if ids:
        technologies = db.scalars(select(Technology).where(Technology.id.in_(ids))).all()
        missing = ids - {t.id for t in technologies}
        if missing:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                f"Tecnologia(s) não encontrada(s): {sorted(missing)}",
            )

    project = Project(
        title=data.title,
        description=data.description,
        repository_url=data.repository_url,
        demo_url=data.demo_url,
        profile=profile,
        technologies=list(technologies),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.scalars(select(Project).order_by(Project.id)).all()
