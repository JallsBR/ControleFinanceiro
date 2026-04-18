# Controle Financeiro

Aplicação web de **controlo financeiro pessoal** com registo de entradas, saídas, categorias, metas, reservas e investimentos, mais áreas de apoio à **consultoria** (vínculo gerente–cliente) e **mensagens internas** entre utilizadores autorizados (equipa de suporte, gerentes e clientes em consultoria ativa). O frontend é **Vue 3** e o backend **Django REST**; os dados financeiros são **por utilizador** (`created_by`). O MySQL **não é partilhado** entre ambientes: ao clonar o repositório, configure a sua instância e o `.env`.

---

## Stack

| Camada    | Tecnologia |
|-----------|------------|
| Backend   | Django 5.2, Django REST Framework, Simple JWT, django-filter, django-cors-headers |
| Banco     | MySQL (variáveis de ambiente) |
| Admin     | Django Admin com tema Jazzmin |
| Frontend  | Vue 3, Vite 7, Vue Router, **Vuex**, PrimeVue (tema Aura), Axios |
| Execução  | Docker (backend + MySQL) + Node (frontend); ou venv em `api/` sem Docker |

---

## Estrutura do projeto

```
ControleFinanceiro/
├── .env                 # Variáveis de ambiente (não versionado; use .env.example como base)
├── .env.example         # Modelo de configuração
├── docker-compose.yml   # MySQL + Django (portas 3307, 8001)
├── Dockerfile           # Imagem do backend
├── package.json         # Scripts (Docker + frontend)
├── docs/ai/             # Contextos para documentação e assistentes (finanças, utilizadores, avisos)
├── api/                 # Backend Django
│   ├── app/             # Settings, URLs, WSGI, utilitários partilhados
│   ├── users/           # Auth (JWT), modelo User, consultoria (vínculo gerente–cliente)
│   ├── financas/        # Categorias, movimentações, metas, reservas, investimentos, dashboard
│   ├── avisos/          # Mensagens internas (inbox/threads), solicitações de consultoria
│   ├── manage.py
│   └── requirements.txt
└── front/               # Frontend Vue (Vite)
    ├── .env.example     # Exemplo com VITE_API_URL (copie para .env se quiser sobrescrever)
    └── ...
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
- Para **Docker:** `DB_NAME`, `DB_USER`, `DB_PASSWORD` devem bater com `docker-compose.yml` (ex.: `controle_db`, `user`, `password`). `DB_HOST=db` e `DB_PORT=3306` são usados dentro do container; o MySQL fica exposto na porta **3307** no host.

O backend usa `python-dotenv` e carrega o `.env` da raiz. O `docker-compose` também injeta variáveis de banco para o container.

### 2. Rodar com Docker (recomendado)

Backend (Django) e banco (MySQL) sobem em containers. O frontend continua na sua máquina (Node).

**Requisitos:** Docker e Docker Compose instalados.

```bash
# Na raiz do projeto
npm install
npm run docker:up:build   # primeira vez: builda a imagem e sobe MySQL + Django
# ou: npm run dev          # sobe Docker + frontend juntos (concurrently)
```

- **MySQL:** porta **3307** no host (evita conflito com outro MySQL). Dados persistem em `./mysql_data/` (não versionado).
- **Django (API):** porta **8001** → `http://127.0.0.1:8001` e `http://localhost:8001`.

Dentro do container, rode as migrations e crie um superusuário:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

O superusuário acessa o **admin** em `http://127.0.0.1:8001/admin/`.

### 3. Frontend (Vue)

Na **raiz do projeto**:

```bash
npm run frontend
# ou, para subir Docker + front juntos: npm run dev
```

- **App:** `http://localhost:5174` (Vite na porta 5174).
- Se quiser mudar a URL da API, crie `front/.env` a partir de `front/.env.example` e defina `VITE_API_URL`.

### 4. Rodar sem Docker (opcional)

**Banco:** use um MySQL local. No `.env` use `DB_HOST=localhost` e `DB_PORT=3306` (ou 3307 se outro MySQL usar 3306).

**Backend:**

```bash
cd api
python -m venv venv
source venv/bin/activate   # Linux/macOS; no Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

**Branch `feature/auto-db-per-user`:** o usuário MySQL em `DB_USER` precisa de **CREATE DATABASE**. Ver `docs/branch-auto-db-per-user.md`.

---

## Scripts (raiz do projeto)

| Comando              | Descrição |
|----------------------|------------|
| `npm run dev`        | Sobe Docker (MySQL + Django) e frontend (Vite) juntos |
| `npm run docker:up`  | Sobe apenas os containers (MySQL + Django) |
| `npm run docker:up:build` | Igual ao anterior, forçando rebuild da imagem |
| `npm run docker:down`| Para e remove os containers |
| `npm run docker:clean` | Remove containers/imagem do `web` (use antes de `docker:up:build` se aparecer erro `ContainerConfig`) |
| `npm run backend`    | Sobe apenas os containers (equivalente a `docker-compose up web`) |
| `npm run frontend`   | Sobe apenas o frontend Vue (Vite) |

---

## URLs principais

| Uso              | URL |
|------------------|-----|
| App (interface)  | `http://localhost:5174` |
| API (base)       | `http://127.0.0.1:8001/api/v1/` |
| Admin (Django)   | `http://127.0.0.1:8001/admin/` |

### API – Autenticação (`/api/v1/auth/`)

- `POST /api/v1/auth/signin` – login (`login`: e-mail ou nome de usuário + `password`) → retorna `user`, `access`, `refresh` (aceita também o campo legado `email` no lugar de `login`)
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

### API – Avisos (`/api/v1/avisos/`)

- `mensagens/` – listagem e criação (threads via `resposta` / `thread_root_id`); filtros: `nome`, `q`, `thread_root_id`, `lido`, `star`, etc.
- `mensagens/<id>/` – detalhe, atualização parcial (ex.: `star`, `lido`), eliminação (só remetente)
- `mensagens/conversas/` – inbox agregado por thread (query: `nome`, `q`, `favorita`)
- `mensagens/threads/<thread_root_id>/marcar-lidas/` – POST para marcar lidas no contexto atual
- `mensagens/nao-lidas/` – contagem para badge
- `mensagens/destinatarios/` – utilizadores que o remetente pode escolher (regras em `mensagens_permissoes.py`)
- `solicitacoes-consultoria/` – pedidos de vínculo consultoria (list/create e detalhe)

Regras de negócio, filtros e padrões por módulo estão em **`docs/ai/`** (`contexto-financas.md`, `contexto-usuarios.md`, `contexto-avisos.md`).

---

## Resumo rápido (com Docker)

1. Copiar `.env.example` para `.env` e configurar `SECRET_KEY` (e conferir `DB_*` para bater com o `docker-compose.yml`).
2. Na raiz: `npm install` e `npm run docker:up:build` (ou `npm run dev` para subir Docker + frontend).
3. Rodar migrations e criar superusuário: `docker-compose exec web python manage.py migrate` e `createsuperuser`.
4. App em `http://localhost:5174`; API e admin em `http://127.0.0.1:8001` e `http://127.0.0.1:8001/admin/`.
