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

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routers import profiles, technologies, projects
from app.database import engine, Base

# Cria as tabelas no banco SQLite local (se ainda não existirem)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DevShowcase API",
    description="API RESTful para vitrine de projetos de desenvolvedores",
    version="2.0.0"
)

# Exception Handler Global para HTTP 404, 400, etc.
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "sucesso": False,
            "codigo": exc.status_code,
            "mensagem": exc.detail,
            "caminho": str(request.url.path)
        },
    )

# Exception Handler Global para Validação de Dados (400 Bad Request)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    erros = []
    for erro in exc.errors():
        campo = " -> ".join([str(x) for x in erro["loc"] if x != "body"])
        erros.append(f"Campo '{campo}': {erro['msg']}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "sucesso": False,
            "codigo": 400,
            "mensagem": "Erro de validação nos dados enviados.",
            "detalhes": erros,
            "caminho": str(request.url.path)
        },
    )

# Inclusão dos Roteadores
app.include_router(profiles.router)
app.include_router(technologies.router)
app.include_router(projects.router)