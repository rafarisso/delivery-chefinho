# Backend - FastAPI

API para registrar despesas, fechar semanas e gerar relatórios.

## Variáveis de ambiente

| Variável | Descrição |
| --- | --- |
| `DATABASE_URL` | URL Postgres (formato `postgresql+psycopg://`) |
| `SUPABASE_URL` | Endpoint do projeto Supabase |
| `SUPABASE_ANON_KEY` | Chave anônima (útil para futuras integrações) |
| `SUPABASE_SERVICE_ROLE_KEY` | Chave Service Role usada para uploads |
| `SUPABASE_BUCKET` | Bucket do Storage (default `receipts`) |
| `ALLOWED_ORIGINS` | URLs permitidas em CORS (ex.: `https://softwarecustosedespesas.netlify.app,http://localhost:5173`) |
| `ADMIN_TOKEN` | Token usado nas rotas protegidas |
| `TZ` | Fuso horário da aplicação (`America/Sao_Paulo`) |

## Como rodar

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate  # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # ajuste ADMIN_TOKEN e ALLOWED_ORIGINS
python -m init_db     # cria tabelas e parceiros padrão
uvicorn main:app --host 0.0.0.0 --port 8000
```

Teste rápido: `curl http://localhost:8000/health` deve retornar `{"status":"ok","tz":"America/Sao_Paulo"}`.

## Supabase

- Banco e Storage são configurados via variáveis de ambiente.
- Bucket padrão `receipts` deve ser público para servir recibos.
- `init_db` garante que Rafael e Guilherme estejam cadastrados com divisão 50/50.

## Deploy (Render)

| Item | Valor |
| --- | --- |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Pós-deploy | Abrir shell e executar `python -m init_db` |

Defina no serviço as variáveis `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `ALLOWED_ORIGINS`, `ADMIN_TOKEN` e `TZ`.

## Testes

```bash
pytest
```

Os testes cobrem os cálculos de fechamento semanal em `services/settlement.py`.
