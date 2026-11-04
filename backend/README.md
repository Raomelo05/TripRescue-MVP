# Backend: API, autenticacao e persistencia

A API usa FastAPI e SQLAlchemy. SQLite e o padrao local; PostgreSQL usa `DATABASE_URL` (`postgresql+psycopg://...`). A configuracao carrega o `.env` na raiz do repositorio sem substituir variaveis exportadas. Configure `SECRET_KEY` no ambiente com um valor aleatorio forte; nao ha segredo padrao e nenhum segredo real deve ser versionado. JWTs HS256 expiram em 30 minutos.

## Executar

Na pasta `backend/`:

```bash
python -m pip install -e ".[dev]"
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Para validar a API e o schema local:

```bash
python -m pytest
python -m alembic upgrade head
```

## Contratos

- `POST /auth/register` e `POST /auth/login` recebem `{ "email": "...", "password": "..." }` e retornam `{ "access_token": "...", "token_type": "bearer", "user": { "id": "...", "email": "..." } }`.
- E-mails sao removidos de espacos laterais e convertidos para minusculas. Senhas sao armazenadas com Argon2id. Cadastro duplicado retorna `409`; login invalido retorna a mesma resposta `401` sem revelar se a conta existe.
- Envie JWTs em `Authorization: Bearer <token>`. O segredo vem de `SECRET_KEY`.
- `GET /trips` lista viagens do usuario autenticado; `POST /trips` cria uma viagem e recebe `{ "title": "...", "destination": "...", "starts_on": "YYYY-MM-DD", "ends_on": "YYYY-MM-DD" }`.
- `GET /trips/{id}`, `PATCH /trips/{id}` e `DELETE /trips/{id}` operam somente nas viagens do usuario autenticado. Viagem inexistente ou de outro usuario retorna `404`. PATCH aceita qualquer subconjunto nao vazio dos campos da viagem.
- Datas invalidas ou `ends_on` anterior a `starts_on` retornam `422`.

Os modelos SQLAlchemy ficam em `app/db/models.py`; as migracoes existentes ja incluem usuarios e viagens. Use Alembic para futuras alteracoes de schema e nao use `create_all()` em producao. Dados privados devem sempre ser consultados no escopo do usuario autenticado.
