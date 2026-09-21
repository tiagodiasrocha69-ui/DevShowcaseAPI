# DevShowcase API

Backend da plataforma **DevShowcase** — vitrine de perfis, projetos e tecnologias de desenvolvedores.

**Stack:** Python 3.11+, FastAPI, SQLAlchemy 2, SQLite, Pydantic v2.

## Como rodar

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Documentação Swagger: http://127.0.0.1:8000/docs

O banco `devshowcase.db` (SQLite) é criado automaticamente na primeira execução.

## Modelo de dados

- **Profile** 1 : N **Project**
- **Project** N : N **Technology** (tabela `project_technology`)
- **Project** 1 : N **Feedback**

## Endpoints

| Método | Rota                  | Descrição                    | Sucesso |
|--------|-----------------------|------------------------------|---------|
| POST   | /api/profiles         | Cadastra perfil              | 201     |
| GET    | /api/profiles/{id}    | Busca perfil por id          | 200     |
| POST   | /api/technologies     | Cadastra tecnologia          | 201     |
| GET    | /api/technologies     | Lista tecnologias            | 200     |
| POST   | /api/projects         | Cadastra projeto             | 201     |
| GET    | /api/projects         | Lista projetos               | 200     |

Erros: `422` (validação), `404` (não encontrado), `409` (duplicado).

### Exemplos de corpo (JSON)

**POST /api/profiles**
```json
{
  "name": "Tiago Silva",
  "email": "tiago@email.com",
  "bio": "Estudante de Desenvolvimento de Sistemas",
  "github_url": "https://github.com/tiago"
}
```

**POST /api/technologies**
```json
{ "name": "Python" }
```

**POST /api/projects**
```json
{
  "title": "Meu Portfólio",
  "description": "Site pessoal com meus projetos",
  "repository_url": "https://github.com/tiago/portfolio",
  "profile_id": 1,
  "technology_ids": [1]
}
```

## Testes automatizados

```bash
pytest
```
"# DevShowcaseAPI"  
