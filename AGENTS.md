# Instruções do agente

Antes de implementar uma tarefa, leia `README.md`, `docs/DECISIONS.md` e as partes relevantes de `docs/PRD.md`. Consulte o código atual e preserve alterações que não pertencem à tarefa.

## Direção do projeto

- O MVP atende web e mobile. Use o app Expo, React Native, TypeScript e Expo Router em `frontend/`.
- A API do MVP usa FastAPI. SQLite é o banco local; PostgreSQL é o banco de produção.
- Cadastro e login usam senha. Armazene senhas com hash apropriado e valide tokens nos endpoints privados.
- Todo dado privado deve ser consultado ou alterado somente no escopo do usuário autenticado.
- Siga as regras do PRD: explique incertezas, não invente dados ou ações externas e priorize segurança física.

## Como trabalhar

- Faça a menor mudança completa que atende ao pedido e siga os padrões e dependências já presentes.
- Não reintroduza decisões substituídas do PRD v2.0, como Vite para o frontend ou ausência de autenticação no MVP.
- Se uma tarefa exigir uma decisão ainda pendente, confira a documentação e registre a decisão em `docs/DECISIONS.md` quando ela afetar a arquitetura ou o escopo.
- Mantenha README e exemplos de ambiente coerentes com o código executável. Nunca grave segredos em arquivos versionados.
- Ao concluir, informe o que mudou e quais verificações foram feitas ou ficaram pendentes.
