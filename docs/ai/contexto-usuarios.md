# Contexto da aplicação – Utilizadores

## Objetivo

Gerir autenticação e cadastro de utilizadores na aplicação (finanças, mensagens e restantes módulos). O modelo **`User`** e o vínculo **`Consultoria`** (gerente–cliente) são também base para as **regras de destinatários** das mensagens internas; ver **`contexto-avisos.md`**.

A autenticação é baseada em:
- E-mail **ou** nome de usuário + senha
- JWT (access + refresh token)
- Controle stateless
- **2FA opcional por e-mail** (OTP de 6 dígitos; desligado por padrão)

---

## Model

Modelo customizado baseado em AbstractUser.

Campos principais em `users.models.User`: `username` (único, validador Unicode), `email` (único), `tenant_db_name` (multi-tenant), `two_factor_enabled` (bool, default `False`), `pagina_inicial`.

Modelo `TwoFactorChallenge` (banco **default**): desafio OTP de login com `id` UUID, `code_hash`, `expires_at`, `consumed_at`, `attempts`. O código em claro **nunca** é persistido.

Regras importantes:

- Email é único.
- Username é único (campo explícito no modelo, alinhado ao AbstractUser).
- O campo username continua sendo obrigatório.
- __str__ retorna o username.
- Ordering padrão: username.

---

## Autenticação

A autenticação de baixo nível é feita via classe `Authentication`; a orquestração de login/2FA mora em `users.services`.

### Signin

Método de baixo nível:
    Authentication.signin(login, password)

Serviço de API:
    users.services.autenticar_signin(login=..., password=...)

O parâmetro `login` é o identificador digitado: **e-mail** (comparação case-insensitive) **ou** **username** (case-insensitive).

Fluxo:

1. Busca usuário por `email__iexact=login` ou `username__iexact=login`.
2. Se não existir → AuthenticationFailed('Credenciais incorretas')
3. Valida senha com check_password.
4. Se inválida → AuthenticationFailed('Credenciais incorretas')
5. Se `two_factor_enabled` for **False** → gera JWT e retorna `user`, `access`, `refresh`.
6. Se `two_factor_enabled` for **True** → cria `TwoFactorChallenge`, envia e-mail HTML (código + link mágico) via `financas@o5o.tech`, retorna `{ "requires_2fa": true, "challenge_id": "<uuid>" }` **sem** tokens.

A view `Signin` aceita `login` no JSON; o campo legado `email` é aceito como alias do identificador.

### Verificação 2FA

    POST /api/v1/auth/2fa/verify
    Body: `{ "challenge_id": "<uuid>", "code": "123456" }`
    ou `{ "challenge_id": "<uuid>", "link_token": "<token-do-link>" }`

Link no e-mail: `{FRONTEND_URL}/auth/2fa-link?c=<challenge_id>&t=<link_token>` (rota pública que chama o verify e grava o JWT).

Serviço: `users.services.verificar_otp_login`.

Regras: OTP 6 dígitos **ou** link mágico de uso único, TTL 10 min, máx. 5 tentativas; hashes com `make_password`/`check_password`. Sucesso → JWT + `user`.

### Toggle 2FA no perfil

`PATCH /api/v1/auth/user` com `two_factor_enabled` exige `current_password` quando o valor muda.

### Recuperação de senha

    POST /api/v1/auth/password-reset/request
    Body: `{ "login": "email-ou-username" }`

Sempre responde a mesma mensagem genérica (anti-enumeração). Se o usuário existir e estiver ativo, cria `PasswordResetChallenge` e envia e-mail HTML (remetente `financas@o5o.tech`) com link:

`{FRONTEND_URL}/auth/redefinir-senha?c=<challenge_id>&t=<token>`

    POST /api/v1/auth/password-reset/confirm
    Body: `{ "challenge_id", "token", "new_password", "new_password_confirm?" }`

TTL 30 minutos; token hasheado; senha validada com validators do Django.

---

### Signup

Método:
    Authentication.signup(username, email, password)

Validações:

- username não pode ser null ou vazio
- email não pode ser null ou vazio
- password não pode ser null ou vazio
- email deve ser único
- username deve ser único

Criação:

- Utiliza User.objects.create_user()
- Senha é automaticamente criptografada

Retorna:
- usuário criado

---

## Política de Logout

A aplicação utiliza JWT (stateless), portanto o backend não mantém sessão ativa.

Existem duas estratégias possíveis:

### Estratégia adotada: Blacklist de Refresh Token

- O logout é feito via endpoint POST /logout
- O refresh token enviado é invalidado usando blacklist
- O access token permanece válido até expirar

Configuração necessária:

INSTALLED_APPS:
    'rest_framework_simplejwt.token_blacklist'

Comportamento:

1. Usuário envia refresh token no body
2. Backend executa token.blacklist()
3. Token não pode mais ser reutilizado

Motivação:

- Impedir reutilização indevida do refresh token
- Aumentar segurança contra roubo de token
- Garantir encerramento de sessão real

---

## Endpoints

Base: `/api/v1/auth/`

| Método | Caminho | Descrição |
|--------|---------|------------|
| POST   | `/api/v1/auth/signin`       | Login (`login` + senha). Sem 2FA → user, access, refresh. Com 2FA → `requires_2fa` + `challenge_id` |
| POST   | `/api/v1/auth/2fa/verify`   | Conclui login com OTP (`challenge_id` + `code`) → user, access, refresh |
| POST   | `/api/v1/auth/password-reset/request` | Solicita e-mail de redefinição (`login`) |
| POST   | `/api/v1/auth/password-reset/confirm` | Confirma token e define `new_password` |
| POST   | `/api/v1/auth/signup`       | Cadastro de usuário |
| POST   | `/api/v1/auth/logout`       | Invalida refresh token (body: `refresh`) |
| POST   | `/api/v1/auth/token/refresh/`| Renova access token (body: `refresh`) |
| GET    | `/api/v1/auth/user`         | Dados do usuário autenticado (JWT), inclui `two_factor_enabled` |
| PATCH  | `/api/v1/auth/user`         | Atualiza perfil; toggle 2FA exige `current_password` |

---

## Permissões

- Signin → AllowAny
- 2FA verify → AllowAny
- Signup → AllowAny
- Logout → IsAuthenticated
- GetUser / PatchUser → IsAuthenticated

---

## Serialização

UserSerializer expõe:

- id
- username
- first_name
- last_name
- email
- is_staff / is_superuser / is_gerente
- pagina_inicial
- two_factor_enabled
- admin_capabilities (só staff)

Não expõe:

- password
- groups
- permissions

---

## Segurança

- Senhas armazenadas com hash (create_user)
- Validação via check_password
- Autenticação baseada em JWT
- Blacklist de refresh token no logout
- Rotas protegidas com IsAuthenticated
- OTP 2FA hasheado; rate limit em signin e 2fa/verify (`auth_signin`, `auth_2fa_verify`)
- E-mail via `integrations/email/` (remetente `DEFAULT_FROM_EMAIL`, tipicamente `financas@o5o.tech`)

---

## Padrões do Projeto

- Toda entidade da aplicação (ex: Movimentação) possui FK created_by
- Sempre usar request.user para vincular dados
- Nunca confiar em ID enviado pelo frontend para associar usuário
- Sempre usar permission_classes adequadas

---

## Melhorias Futuras

- Implementar autenticação via authenticate() com backend customizado para email
- Implementar verificação de email
- Separar camada de domínio/serviço (parcialmente feito em `users.services`)
- Implementar controle de múltiplas sessões

---

## Documentação relacionada

- **`contexto-financas.md`** – recursos em `/api/v1/financas/` e filtro por `created_by`.
- **`contexto-avisos.md`** – mensagens internas, threads e endpoints em `/api/v1/avisos/`.
