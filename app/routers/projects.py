from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/projects", tags=["Projetos"])

# -------------------------------------------------------------
# CADASTRAR PROJETO (POST)
# -------------------------------------------------------------
@router.post("", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def criar_projeto(projeto: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # 1. Verifica se o perfil existe
    perfil = db.query(models.Profile).filter(models.Profile.id == projeto.profile_id).first()
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Perfil com ID {projeto.profile_id} não encontrado."
        )

    # 2. Instancia o novo projeto
    novo_projeto = models.Project(
        title=projeto.title,
        description=projeto.description,
        repository_url=projeto.repository_url,
        profile_id=projeto.profile_id,
        upvotes=0
    )

    # 3. Busca e vincula as tecnologias se forem enviadas no body
    if hasattr(projeto, "technology_ids") and projeto.technology_ids:
        tecnologias = db.query(models.Technology).filter(
            models.Technology.id.in_(projeto.technology_ids)
        ).all()
        novo_projeto.technologies = tecnologias

    db.add(novo_projeto)
    db.commit()
    db.refresh(novo_projeto)

    # Atribui valor inicial para evitar erro no schema de resposta
    novo_projeto.average_rating = 0.0

    return novo_projeto


# -------------------------------------------------------------
# 1. LISTAR PROJETOS (GET COM FILTRO E PAGINAÇÃO)
# -------------------------------------------------------------
@router.get("", response_model=List[schemas.ProjectResponse])
def listar_projetos(
    technology: Optional[str] = Query(None, description="Filtrar por nome da tecnologia"),
    skip: int = Query(0, ge=0, description="Número de registros a pular"),
    limit: int = Query(10, ge=1, le=100, description="Quantidade de registros por página"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Project)

    if technology:
        query = query.join(models.Project.technologies).filter(
            models.Technology.name.ilike(f"%{technology}%")
        )

    projetos = query.offset(skip).limit(limit).all()

    for p in projetos:
        if hasattr(p, "feedbacks") and p.feedbacks:
            p.average_rating = round(sum(f.rating for f in p.feedbacks) / len(p.feedbacks), 2)
        else:
            p.average_rating = 0.0

    return projetos


# -------------------------------------------------------------
# 2. CADASTRAR FEEDBACK
# -------------------------------------------------------------
@router.post("/{project_id}/feedbacks", response_model=schemas.FeedbackResponse, status_code=status.HTTP_201_CREATED)
def criar_feedback(
    project_id: int, 
    feedback: schemas.FeedbackCreate, 
    db: Session = Depends(get_db)
):
    projeto = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not projeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Projeto com ID {project_id} não foi encontrado."
        )

    novo_feedback = models.Feedback(
        author_name=feedback.author_name,
        comment=feedback.comment,
        rating=feedback.rating,
        project_id=project_id
    )
    db.add(novo_feedback)
    db.commit()
    db.refresh(novo_feedback)
    return novo_feedback


# -------------------------------------------------------------
# 3. INCREMENTAR UPVOTE
# -------------------------------------------------------------
@router.put("/{project_id}/upvote")
def incrementar_upvote(project_id: int, db: Session = Depends(get_db)):
    projeto = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not projeto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Projeto com ID {project_id} não foi encontrado."
        )

    projeto.upvotes = (projeto.upvotes or 0) + 1
    db.commit()
    db.refresh(projeto)

    return {
        "sucesso": True,
        "mensagem": "Upvote registrado com sucesso!",
        "project_id": project_id,
        "total_upvotes": projeto.upvotes
    }