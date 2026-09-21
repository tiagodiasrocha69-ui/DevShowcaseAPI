from datetime import datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    HttpUrl,
    StringConstraints,
    TypeAdapter,
)

# ---------- Tipos reutilizáveis com validação ----------

# Texto obrigatório: remove espaços nas pontas e não aceita vazio
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

_url_adapter = TypeAdapter(HttpUrl)


def _check_url(value: str) -> str:
    _url_adapter.validate_python(value)  # lança erro se a URL for inválida
    return value


# URL válida (http/https), mantida como string para salvar no banco
UrlStr = Annotated[str, AfterValidator(_check_url)]


# ---------- Technology ----------
class TechnologyCreate(BaseModel):
    name: NonEmptyStr = Field(max_length=80, examples=["Python"])


class TechnologyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# ---------- Profile ----------
class ProfileCreate(BaseModel):
    name: NonEmptyStr = Field(max_length=120, examples=["Tiago Silva"])
    email: EmailStr
    bio: str | None = None
    avatar_url: UrlStr | None = None
    github_url: UrlStr | None = None
    linkedin_url: UrlStr | None = None


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    bio: str | None
    avatar_url: str | None
    github_url: str | None
    linkedin_url: str | None


# ---------- Feedback ----------
class FeedbackCreate(BaseModel):
    author_name: NonEmptyStr = Field(max_length=120)
    comment: NonEmptyStr
    rating: int = Field(ge=1, le=5)


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_name: str
    comment: str
    rating: int
    created_at: datetime


# ---------- Project ----------
class ProjectCreate(BaseModel):
    title: NonEmptyStr = Field(max_length=150, examples=["Meu Portfólio"])
    description: str | None = None
    repository_url: UrlStr | None = None
    demo_url: UrlStr | None = None
    profile_id: int = Field(gt=0)
    technology_ids: list[int] = Field(default_factory=list)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    repository_url: str | None
    demo_url: str | None
    created_at: datetime
    profile_id: int
    technologies: list[TechnologyResponse]
    feedbacks: list[FeedbackResponse]
