
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import os






BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-dev-key-change-in-prod'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'avis',
]

MIDDLEWARE = [
    
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS pour Vercel
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://agentreponse.vercel.app",
    "https://agentreponse-3e18fojfl-bouyesaturnins-projects.vercel.app",
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ALLOW_ALL_ORIGINS = True  # ← remplace True par False

ROOT_URLCONF = 'avis_agent.urls'

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates','DIRS': [],'APP_DIRS': True,'OPTIONS': {'context_processors': ['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages',]},}]

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3','NAME': BASE_DIR / 'db.sqlite3',}}

GMAIL_USER = os.environ.get('GMAIL_USER', '').strip()
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD', '').strip()
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', '').strip()
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', '').strip()



STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')