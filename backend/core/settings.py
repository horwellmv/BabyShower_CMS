import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR.parent / '.env')

# =============================================================================
# CORE SETTINGS
# =============================================================================

DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Security: no insecure fallback in production
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-only-fallback-key'
    else:
        raise ValueError(
            "The SECRET_KEY environment variable is required in production. "
            "Generate one with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
        )

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

INSTALLED_APPS = [
    'jazzmin',  # Jazzmin must be before admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom apps
    'apps.invitations',
    
    # Tailwind CSS
    'tailwind',
    'theme',
    'django_browser_reload',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom guest session auth middleware
    'apps.invitations.middleware.GuestSessionMiddleware',
    
    # Browser reload
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

TAILWIND_APP_NAME = 'theme'

NPM_BIN_PATH = os.getenv('NPM_BIN_PATH', r"C:\Program Files\nodejs\npm.cmd")

INTERNAL_IPS = [
    "127.0.0.1",
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR.parent, 'frontend', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# =============================================================================
# DATABASE
# =============================================================================
# Uses DATABASE_URL env var for PostgreSQL in production.
# Falls back to SQLite for local development.

DATABASE_URL = os.getenv('DATABASE_URL', '')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
elif not DEBUG:
    raise ValueError(
        "DATABASE_URL environment variable is required in production (DEBUG=False). "
        "Please link the PostgreSQL service to your app in Railway variables."
    )
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =============================================================================
# AUTH PASSWORD VALIDATORS
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# =============================================================================

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR.parent, 'frontend', 'assets'),
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# =============================================================================
# MEDIA FILES (uploaded by Admin)
# =============================================================================

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media')

# =============================================================================
# STORAGE BACKENDS
# =============================================================================

# Supabase Storage config
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET', 'media')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Static files storage: use CompressedStaticFilesStorage to prevent 500 errors if a static manifest entry is missing
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Media storage: Supabase in production, local filesystem in development
if SUPABASE_URL and SUPABASE_KEY:
    STORAGES["default"] = {
        "BACKEND": "core.storage_backends.SupabaseStorage",
    }
else:
    STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # CSRF trusted origins for Railway
    CSRF_TRUSTED_ORIGINS = [
        'https://*.railway.app',
        'https://*.up.railway.app',
    ]
    csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS')
    if csrf_origins_env:
        CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in csrf_origins_env.split(',') if origin.strip()])


# =============================================================================
# JAZZMIN (Admin Panel)
# =============================================================================

JAZZMIN_SETTINGS = {
    "site_title": "AdharaBS",
    "site_header": "AdharaBS",
    "site_brand": "Adhara BabyShower",
    "welcome_sign": "Bienvenidos a la administración de Adhara",
    "copyright": "Desarrollado por <a href='https://muval.net' target='_blank' style='color: #785252; font-weight: bold; text-decoration: underline;'>Muval.net</a>",
    "search_model": ["invitations.Guest"],
    "topmenu_links": [],
    "show_sidebar": True,
    "navigation_expanded": True,
    "show_version": False,
    "icons": {
        "invitations.Guest": "fas fa-user-friends",
        "invitations.Gift": "fas fa-gift",
        "invitations.GiftReservation": "fas fa-bookmark",
        "invitations.GalleryImage": "fas fa-images",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_layout": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "cerulean"
}
