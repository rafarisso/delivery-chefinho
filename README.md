# Sistema de Gastos Delivery

Monorepo com backend FastAPI e frontend React para controle de despesas semanais do delivery.

## Desenvolvimento local

1. Duplique `backend/.env.example` para `backend/.env` e ajuste os valores reais antes de subir os servicos.
2. Instale as dependencias do backend: `pip install -r backend/requirements.txt`.
3. Instale as dependencias do frontend: dentro da pasta `frontend/` execute `npm install`.
4. Inicialize o banco quando necessario com `python -m init_db` (execute dentro de `backend/`).
5. Rode a API localmente com `uvicorn main:app` a partir da pasta `backend/`.

## Supabase

- Use os valores de `backend/.env.example` (`DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`).
- Crie o bucket publico `receipts`: Storage > Create bucket > `receipts` > Public ON.
- Garanta que a base esteja vazia antes de rodar o seed inicial.

## Backend (producao)

1. Instale dependencias: `pip install -r backend/requirements.txt`.
2. Defina as variaveis copiando `backend/.env.example` e ajuste `ADMIN_TOKEN` e `ALLOWED_ORIGINS`.
3. Inicialize o banco uma unica vez:
   ```bash
   cd backend
   python -m init_db
   ```
4. Execute o servidor: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
5. Teste com `GET /health` para confirmar `{ "status": "ok", "tz": "America/Sao_Paulo" }`.

## Frontend (Netlify)

- Defina `VITE_API_URL=https://SUA_API_PUBLICA/api`.
- Rode `npm install` e `npm run build` (gera `dist/`).
- O arquivo `frontend/netlify.toml` ja publica `dist/` e faz redirect SPA.

## Testes finais

- Login com a senha igual ao `ADMIN_TOKEN`.
- Criar despesa e enviar recibo (arquivo vai para o bucket `receipts`).
- Gerar exportacoes PDF e CSV na tela de relatorios semanais.

## Deploy no Render (backend)

- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `DATABASE_URL`
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `SUPABASE_ANON_KEY` (opcional para futuras integracoes)
  - `ALLOWED_ORIGINS=https://softwarecustosedespesas.netlify.app,http://localhost:5173`
  - `ADMIN_TOKEN=<defina_um_token_forte>`
  - `TZ=America/Sao_Paulo`
  - `SUPABASE_BUCKET=receipts` (opcional, default `receipts`)
- Pos-deploy:
  ```bash
  # abrir shell do servico no Render
  python -m init_db
  ```
- Verifique manualmente `GET /health` apos o seed.

## Estrutura

```
backend/   # FastAPI + SQLAlchemy + Supabase Storage
frontend/  # Vite + React + TypeScript
```

Consulte `backend/README.md` e `frontend/README.md` para detalhes adicionais de desenvolvimento local.
