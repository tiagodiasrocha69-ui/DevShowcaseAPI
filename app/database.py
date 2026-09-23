import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Obtém a URL do Render ou usa SQLite local por padrão se não existir
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./devshowcase.db")

# Ajusta o prefixo 'postgres://' para 'postgresql://' se necessário (exigência do SQLAlchemy)
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Se for SQLite precisa de connect_args, se for Postgres não precisa
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()