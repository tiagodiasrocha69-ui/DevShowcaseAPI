from fastapi import FastAPI

from app import models  # noqa: F401  (registra as tabelas)
from app.database import Base, engine
from app.routers import profiles, projects, technologies

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DevShowcase API",
    description="API para vitrine de perfis, projetos e tecnologias de desenvolvedores.",
    version="0.1.0",
)

app.include_router(profiles.router)
app.include_router(technologies.router)
app.include_router(projects.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "docs": "/docs"}
