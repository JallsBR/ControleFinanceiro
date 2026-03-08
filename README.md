# Controle Financeiro

Aplicação de controle financeiro pessoal com **frontend Vue 3** e **backend Django REST**. Cada usuário tem seus próprios dados (movimentações, categorias, metas, reservas, investimentos). O banco **não é compartilhado** entre ambientes: ao clonar, configure seu próprio MySQL e `.env`.

---

## Stack

| Camada    | Tecnologia |
|-----------|------------|
| Backend   | Django 5.2, Django REST Framework, Simple JWT, django-filter, django-cors-headers |
| Banco     | MySQL (configurado via variáveis de ambiente) |
| Admin     | Django Admin com tema Jazzmin |
| Frontend  | Vue 3, Vite 7, Vue Router, Pinia, PrimeVue, Axios |
| Execução  | Node (scripts na raiz) + Python (venv em `api/`) |

---

## Estrutura do projeto

```
ControleFinanceiro/
├── .env                 # Variáveis de ambiente (não versionado; use .env.example como base)
├── .env.example         # Modelo de configuração
├── package.json         # Scripts para subir backend + frontend
├── api/                 # Backend Django
│   ├── app/             # Settings, URLs, WSGI
│   ├── users/           # Auth (signin, signup, logout, JWT)
│   ├── financas/        # Categorias, movimentações, metas, reservas, investimentos, dashboard
│   ├── manage.py
│   └── requirements.txt
├── front/               # Frontend Vue (Vite)
└── docs/                # Documentação (contexto de negócio e API)
    └── ai/              # Contexto para desenvolvimento (finanças, usuários)
```

---

## Primeira vez (após clonar)

### 1. Variáveis de ambiente

Na **raiz do projeto**, crie um arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Edite `.env` e preencha pelo menos:

- `SECRET_KEY` – chave secreta do Django (produção: use valor forte e seguro)
- `DB_NAME` – nome do banco MySQL
- `DB_USER` e `DB_PASSWORD` – usuário e senha do MySQL
- `DB_HOST` e `DB_PORT` – host e porta (ex.: `localhost`, `3306`)

O backend usa `python-dotenv` e carrega o `.env` da raiz (a partir de `api/app/settings.py`).

### 2. Banco de dados

Crie o banco MySQL com o nome definido em `DB_NAME` (ex.: `ControleFinaceiro`). As tabelas são criadas pelas migrations do Django; não é necessário compartilhar o banco entre máquinas.

### 3. Backend (API Django)

```bash
cd api
python -m venv venv
.\venv\Scripts\activate.ps1   # Windows PowerShell
# ou: source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

O superusuário criado terá acesso ao **painel admin** (Jazzmin) em `http://127.0.0.1:8000/admin/`.

### 4. Frontend (Vue)

Na **raiz do projeto** (não dentro de `api` nem de `front`):

```bash
npm install
npm run dev
```

O script `npm run dev` sobe os dois servidores com **concurrently**:

- **Django (API):** `http://127.0.0.1:8000`
- **Vue (app):** porta do Vite (em geral `http://localhost:5173`)

Acesse o **app** pela URL que o Vite mostrar no terminal. Para o **admin**, use `http://127.0.0.1:8000/admin/` com o superusuário.

---

## Scripts (raiz do projeto)

| Comando        | Descrição |
|----------------|-----------|
| `npm run dev`  | Sobe backend (Django) e frontend (Vite) juntos |
| `npm run backend`  | Sobe apenas o servidor Django |
| `npm run frontend` | Sobe apenas o frontend Vue |

---

## URLs principais

| Uso              | URL |
|------------------|-----|
| App (interface)  | URL do Vite (ex.: `http://localhost:5173`) |
| API (base)       | `http://127.0.0.1:8000/api/v1/` |
| Admin (Django)   | `http://127.0.0.1:8000/admin/` |

### API – Autenticação (`/api/v1/auth/`)

- `POST /api/v1/auth/signin` – login (email + senha) → retorna `user`, `access`, `refresh`
- `POST /api/v1/auth/signup` – cadastro
- `POST /api/v1/auth/logout` – invalida refresh token (body: `refresh`)
- `POST /api/v1/auth/token/refresh/` – renova access token (body: `refresh`)
- `GET /api/v1/auth/user` – usuário autenticado (requer JWT)

### API – Finanças (`/api/v1/financas/`)

Recursos (todos exigem autenticação JWT; dados filtrados por `created_by`):

- `categorias/` – categorias de movimentação
- `movimentacoes/` – entradas e saídas
- `movimentacoes-recorrentes/` – movimentações recorrentes
- `metas/` – metas financeiras
- `consolidados-mensais/` – consolidados por mês
- `reservas/` – reservas
- `investimentos/` – investimentos
- `icone/` – ícones (ex.: para categorias)
- `dashboard/` – dados para o dashboard

Detalhes de regras de negócio, filtros e padrões estão em `docs/ai/`.

---

## Documentação

- **`docs/ai/contexto-usuarios.md`** – modelo de usuário, autenticação (JWT, signin/signup/logout), endpoints de auth, serialização e segurança.
- **`docs/ai/contexto-financas.md`** – domínio de finanças (movimentações, recorrentes, categorias), regras de negócio, filtros e padrões do projeto.

---

## Resumo rápido

1. Copiar `.env.example` para `.env` e configurar MySQL e `SECRET_KEY`.
2. Criar o banco MySQL.
3. Em `api/`: criar venv, instalar dependências, rodar `migrate` e `createsuperuser`.
4. Na raiz: `npm install` e `npm run dev`.
5. App no endereço do Vite; admin em `http://127.0.0.1:8000/admin/`.
