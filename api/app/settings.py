from datetime import timedelta
from pathlib import Path
import os

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis do .env (raiz do projeto = parent de api/)
load_dotenv(BASE_DIR.parent / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-1q70&1=*ova79vqzky0luwizie3f9vo2sp20yo%-vb3)atuf=u')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
]


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
}

ROOT_URLCONF = 'app.urls'

# CORS: origens explícitas para funcionar com credenciais (cookies/withCredentials)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

# Preflight: headers que o frontend pode enviar
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
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

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=48),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
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