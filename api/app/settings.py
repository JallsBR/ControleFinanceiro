from datetime import timedelta
from pathlib import Path
import os

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis do .env (raiz do projeto = parent de api/)
_root_env = BASE_DIR.parent / ".env"
load_dotenv(_root_env)
# Sobrescreve com .env.local (gitignored) — ex.: DB_HOST=127.0.0.1 para `manage.py` no host
# enquanto o `.env` mantém DB_HOST=db para o serviço `web` no Docker.
_env_local = BASE_DIR.parent / ".env.local"
if _env_local.is_file():
    load_dotenv(_env_local, override=True)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ImproperlyConfigured(f"{name} deve ser um inteiro válido.") from exc


def _env_csv_urls(name: str, default):
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-1q70&1=*ova79vqzky0luwizie3f9vo2sp20yo%-vb3)atuf=u')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost,0.0.0.0",
    ).split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Rest Framework
    'rest_framework',
    'django_filters',
    # Cors headers
    "corsheaders",
    # JWT
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    # Apps
    'users',
    'financas',
    'avisos.apps.AvisosConfig',
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

AUTH_USER_MODEL = 'users.User'


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "app.middleware.DisableCSRFForAPI",
    "django.middleware.csrf.CsrfViewMiddleware",
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'app.middleware_tenant.TenantDatabaseMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if not DEBUG:
    MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_RATES': {
        'auth_signin': '30/hour',
        'auth_2fa_verify': '30/hour',
        'auth_password_reset': '10/hour',
        'auth_password_reset_confirm': '20/hour',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'controlefinanceiro-default',
    },
}

ROOT_URLCONF = 'app.urls'

# CORS: origens via .env (CORS_ALLOWED_ORIGINS=url1,url2). Regex opcional para localhost (Vite em porta variável).
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

_default_cors_origins = [
    # Vite (vite.config.js → 2488; mantém portas antigas por compatibilidade)
    "http://localhost:2488",
    "http://127.0.0.1:2488",
    "http://localhost:2486",
    "http://127.0.0.1:2486",
    "http://localhost:2487",
    "http://127.0.0.1:2487",
    # Vite default / alternativas
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    # vite preview
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

_env_cors_raw = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
_env_cors_list = (
    [item.strip() for item in _env_cors_raw.split(",") if item.strip()]
    if _env_cors_raw
    else []
)

if DEBUG and _env_cors_list:
    # Dev: união env + defaults (sem duplicar). Evita .env só com :2486 bloquear quem abre :5173, etc.
    _seen = set()
    CORS_ALLOWED_ORIGINS = []
    for origin in _env_cors_list + _default_cors_origins:
        if origin not in _seen:
            _seen.add(origin)
            CORS_ALLOWED_ORIGINS.append(origin)
else:
    CORS_ALLOWED_ORIGINS = (
        _env_cors_list if _env_cors_list else list(_default_cors_origins)
    )
# CORS_ALLOW_LOCALHOST_REGEX: se não definido, ativa quando DEBUG=True
_cors_localhost_regex = os.getenv("CORS_ALLOW_LOCALHOST_REGEX")
if _cors_localhost_regex is None or _cors_localhost_regex.strip() == "":
    _use_cors_regex = DEBUG
else:
    _use_cors_regex = _cors_localhost_regex.lower() in ("true", "1", "yes", "on")
CORS_ALLOWED_ORIGIN_REGEXES = (
    [
        r"^http://localhost(:\d+)?$",
        r"^http://127\.0\.0\.1(:\d+)?$",
    ]
    if _use_cors_regex
    else []
)

# Preflight: headers que o frontend pode enviar
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    # Visão staff/gerente no tenant do cliente (APIService + middleware_tenant)
    "x-financas-subject-user",
]
# Headers que o frontend pode ler na resposta (ex.: Authorization com JWT)
CORS_EXPOSE_HEADERS = ["Authorization"]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

_default_db = {
    'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
    'NAME': os.getenv('DB_NAME', 'ControleFinanceiro'),
    'USER': os.getenv('DB_USER', 'root'),
    'PASSWORD': os.getenv('DB_PASSWORD', ''),
    'HOST': os.getenv('DB_HOST', 'localhost'),
    'PORT': os.getenv('DB_PORT', '3307'),
    'OPTIONS': {
        'charset': 'utf8mb4',
    },
}

DATABASES = {
    'default': _default_db.copy(),
    'tenant': _default_db.copy(),  # NAME sobrescrito por request no middleware
}

DATABASE_ROUTERS = ['app.db_router.TenantRouter']


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

if not DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# E-mail (OTP 2FA, etc.).
# Prioridade: EMAIL_BACKEND explícito → SMTP se houver host/user → console em DEBUG.
_email_backend_env = os.getenv("EMAIL_BACKEND", "").strip()
EMAIL_HOST = os.getenv("EMAIL_HOST", "").strip() or "localhost"
EMAIL_PORT = _env_int("EMAIL_PORT", 587)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() in ("true", "1", "yes")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "financas@o5o.tech")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:2488").rstrip("/")

_smtp_configurado = bool(EMAIL_HOST_USER) or (
    EMAIL_HOST not in ("", "localhost", "127.0.0.1")
)
if _email_backend_env:
    EMAIL_BACKEND = _email_backend_env
elif _smtp_configurado:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
elif DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Tempos JWT via .env (ex.: access curto em prod, maior em dev)
_jwt_access_minutes = _env_int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 48 * 60)
_jwt_refresh_days = _env_int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 7)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=_jwt_access_minutes),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=_jwt_refresh_days),
}

JAZZMIN_SETTINGS = {
    "site_header": "Finanças",
    "site_brand": "Finanças",
    "welcome_sign": "Bem-vindo à Finanças",
    "copyright": "Finanças",
    "icons": {
        "auth": "fas fa-users",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "auth.permission": "fas fa-key",
        "auth.userprofile": "fas fa-user",
        "auth.userprofile": "fas fa-user",
        "financas.categoria": "fas fa-money-bill",
        "financas.movimentacao": "fas fa-money-bill",
        "financas.movimentacaorecorrente": "fas fa-money-bill",
        "financas.meta": "fas fa-chart-line",
        "financas.consolidado-mensal": "fas fa-money-bill",
        "financas.icone": "fas fa-icons",
        "users.user": "fas fa-user",
    },

}