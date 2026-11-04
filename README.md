# TripRescue

Assistente de viagem para ajudar viajantes a entender imprevistos, organizar o itinerário e acompanhar um plano de ação seguro.

## Estado

O repositório contém o esqueleto inicial do app universal em `frontend/`. Consulte [docs/DECISIONS.md](docs/DECISIONS.md) para as decisões confirmadas e o próximo passo. O PRD de referência está em [docs/PRD.md](docs/PRD.md) e no PDF original na raiz.

O agente de desenvolvimento deve seguir as instruções de [AGENTS.md](AGENTS.md).

## Direção confirmada pelo usuário

- Disponível na web e em aplicativo móvel.
- Cadastro e login com senha no MVP.
- Usuários registram viagens com datas e destino.
- O assistente orienta o usuário diante de problemas de viagem.

## Arquitetura do MVP

- App web e móvel: Expo, React Native, TypeScript e Expo Router em `frontend/`, compartilhando a maior parte da interface.
- API: FastAPI, conforme a direção técnica do PRD.
- Banco: SQLite no desenvolvimento local; PostgreSQL no ambiente publicado.
- Conta e autorização: autenticação por senha na API. Todo endpoint com dados privados deve obter o usuário pelo token validado e limitar consultas a esse usuário.

## Próxima etapa

O app Expo e a API FastAPI têm esqueletos iniciais. Próximo passo: implementar cadastro/login e o cadastro de viagens como um fluxo vertical completo, protegendo cada registro pelo usuário autenticado.

## Desenvolvimento local

Frontend (requer Node.js e npm):

```bash
cd frontend
npm install
npm run web
```

API (requer Python e as dependências de `backend/pyproject.toml`):

```bash
cd backend
python -m pip install -e .
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Configure `EXPO_PUBLIC_API_URL` no frontend e `DATABASE_URL` no backend quando forem integrados. Use `.env.example` como referência; nunca salve credenciais reais no Git.

O banco local usa SQLite por padrão. Para preparar os testes do backend, instale `python -m pip install -e ".[dev]"` e execute `python -m pytest` dentro de `backend/`. Alterações de schema devem ser versionadas em migrações Alembic; veja [backend/README.md](backend/README.md).
