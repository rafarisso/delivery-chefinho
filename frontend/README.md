# Frontend - React + Vite

SPA em TypeScript que consome a API FastAPI para gerenciar despesas, fechamentos e relatórios.

## Variáveis (`.env` ou Netlify)

```
VITE_API_URL=https://SUA_API_PUBLICA/api
```

## Desenvolvimento local

```bash
npm install
npm run dev
```

Acesse `http://localhost:5173`. O login usa o `ADMIN_TOKEN` configurado no backend.

## Build

```bash
npm run build
npm run preview
```

## Deploy (Netlify)

- Build command: `npm run build`
- Publish directory: `dist`
- `frontend/netlify.toml` já inclui redirect SPA.
- Defina `VITE_API_URL` no painel da Netlify.

## Estrutura principal

```
src/
  services/api.ts      # cliente axios com baseURL em VITE_API_URL
  hooks/useAuth.ts     # contexto de autenticação
  components/
    FileUpload.tsx
    WeekPicker.tsx
  pages/
    Login.tsx
    Despesas.tsx
    Fechamento.tsx
    Relatorios.tsx
    SettlementDetail.tsx
```

Os relatórios utilizam endpoints `/reports/settlements`, `/reports/weekly.csv` e `/reports/weekly.pdf`.

## TODO (futuro)

- Integração direta com Supabase Auth.
- Feedback visual (toast/spinner, libs como Tailwind ou Chakra UI).
- Offline/PWA e envio automático dos relatórios.
