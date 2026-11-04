# Backend: persistência

Os modelos SQLAlchemy ficam em `app/db/models.py`; `app/db/session.py` configura o engine e a sessão. O padrão local é SQLite e a API publicada deve usar PostgreSQL por `DATABASE_URL` (`postgresql+psycopg://...`). A configuração carrega o `.env` da raiz do repositório, sem sobrescrever variáveis já exportadas.

Execute na pasta `backend/`:

```bash
python -m pip install -e ".[dev]"
python -m alembic upgrade head
python -m pytest
```

Depois de alterar os modelos, gere e revise a migração:

```bash
python -m alembic revision --autogenerate -m "descricao da alteracao"
```

O schema inicial cobre contas, viagens, trechos, compromissos, incidentes, planos/tarefas e registros textuais de nota, protocolo e histórico. Todo registro privado deve ser consultado no escopo do usuário autenticado; as chaves estrangeiras compostas também bloqueiam vínculos acidentais entre usuários no banco. `password_hash` guarda somente o hash, nunca a senha original. Em produção, use migrações; não use `create_all()`.
