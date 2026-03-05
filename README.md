# ControleFinanceiro

App de Controle Financeiro (frontend Vue + backend Django REST).

O banco de dados **não é compartilhado**. Ao clonar o repositório, cada usuário deve criar o próprio banco e o usuário administrador através das migrations e do comando de criação de superusuário.

---

## Primeira vez (após clonar)

### 1. Backend (API Django)

```bash
cd api
python -m venv venv
.\venv\Scripts\activate.ps1   # Windows PowerShell
# ou: source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser (pode criar o seu)
```
Para teste já vem com:
- **Usuário:** `admim`
- **Senha:** `12345`
- **E-mail:** `admin@email.com`

Esse superusuário terá acesso ao painel admin em `http://127.0.0.1:8000/admin/`.

### 2. Frontend (Vue)

Na pasta **raiz do projeto** (não dentro de `api` nem de `front`):

```bash
npm install
npm run dev
```

O script `npm run dev` sobe os dois servidores:

- **Django (API):** `http://127.0.0.1:8000`
- **Vue (app):** na porta do Vite (em geral `http://localhost:5173`)

Acesse o **app** pela URL que o Vite mostrar no terminal (ex.: `http://localhost:5173`).

Para acessar o **painel administrativo** (admin do Django), use:

- **URL:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Login:** superusuário criado no passo 1 (ex.: `admim` / `12345`)

---

## Resumo

| O quê              | Como                |
|--------------------|---------------------|
| Rodar projeto todo | Na pasta raiz: `npm run dev` |
| App (interface)    | URL do Vite (ex.: `http://localhost:5173`) |
| Admin (Django)     | `http://127.0.0.1:8000/admin/` com o superusuário |
