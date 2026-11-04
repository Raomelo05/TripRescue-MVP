# Decisões do projeto

## Confirmadas

- Produto: assistente de viagem para pessoas que viajam frequentemente.
- Plataformas: web e aplicativo móvel no MVP. Definido pelo usuário em 2026-11-03; atualiza o PRD v2.0.
- Conta: cadastro e login com senha no MVP. Definido pelo usuário em 2026-11-03; atualiza o PRD v2.0.
- Dados básicos de viagem: datas e destino.
- O plano de ação deve se adaptar ao problema relatado.
- Regras de segurança e confiabilidade do PRD continuam válidas: não inventar dados, explicitar incerteza e priorizar segurança física.
- Frontend web e móvel: Expo + React Native + TypeScript + Expo Router. O esqueleto já existe em `frontend/` e será a base compartilhada do MVP.
- API: FastAPI, mantendo a direção técnica do PRD.
- Persistência: SQLite no desenvolvimento local e PostgreSQL no ambiente publicado; a camada de acesso deve permitir ambos.
- Autenticação: cadastro e login por senha na API. Senhas devem ser armazenadas apenas com hash apropriado; tokens devem ser validados em todo endpoint privado.
- Isolamento: cada consulta ou alteração de dado privado deve ser escopada ao usuário autenticado desde o primeiro endpoint.

## Pendentes antes de publicar

- Escolher hospedagem para API e PostgreSQL e validar a configuração de produção.
- Definir política de expiração, renovação e recuperação de conta antes do lançamento público.

## Fonte

Ver [`PRD.md`](PRD.md) e o PDF original na raiz do projeto. As decisões acima atualizam o PRD v2.0 conforme as necessidades confirmadas para o MVP.
