# Contexto da Aplicação - Usuários

## Objetivo

Gerenciar autenticação e cadastro de usuários na aplicação de finanças.

A autenticação é baseada em:
- E-mail **ou** nome de usuário + senha
- JWT (access + refresh token)
- Controle stateless

---

## Model

Modelo customizado baseado em AbstractUser.

Campos principais em `users.models.User`: `username` (único, validador Unicode), `email` (único), `tenant_db_name` (multi-tenant).

Regras importantes:

- Email é único.
- Username é único (campo explícito no modelo, alinhado ao AbstractUser).
- O campo username continua sendo obrigatório.
- __str__ retorna o username.
- Ordering padrão: username.

---

## Autenticação

A autenticação é feita manualmente via classe Authentication.

### Signin

Método:
    Authentication.signin(login, password)

O parâmetro `login` é o identificador digitado: **e-mail** (comparação case-insensitive) **ou** **username** (case-insensitive).

Fluxo:

1. Busca usuário por `email__iexact=login` ou `username__iexact=login`.
2. Se não existir → AuthenticationFailed('Credenciais incorretas')
3. Valida senha com check_password.
4. Se inválida → AuthenticationFailed('Credenciais incorretas')
5. Retorna o usuário autenticado.

A view `Signin` aceita `login` no JSON; o campo legado `email` é aceito como alias do identificador.

Após autenticação:
- Gera JWT via RefreshToken.for_user(user)
- Retorna:
    - user (serializado)
    - refresh token
    - access token

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
| POST   | `/api/v1/auth/signin`       | Login (`login` + senha; e-mail ou username) → user, access, refresh |
| POST   | `/api/v1/auth/signup`       | Cadastro de usuário |
| POST   | `/api/v1/auth/logout`       | Invalida refresh token (body: `refresh`) |
| POST   | `/api/v1/auth/token/refresh/`| Renova access token (body: `refresh`) |
| GET    | `/api/v1/auth/user`         | Dados do usuário autenticado (JWT) |

---

## Permissões

- Signin → AllowAny
- Signup → AllowAny
- Logout → IsAuthenticated
- GetUser → IsAuthenticated

---

## Serialização

UserSerializer expõe:

- id
- username
- last_name
- email

Não expõe:

- password
- is_staff
- is_superuser
- groups
- permissions

---

## Segurança

- Senhas armazenadas com hash (create_user)
- Validação via check_password
- Autenticação baseada em JWT
- Blacklist de refresh token no logout
- Rotas protegidas com IsAuthenticated

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
- Implementar reset de senha
- Adicionar rate limit em signin
- Separar camada de domínio/serviço
- Implementar controle de múltiplas sessões