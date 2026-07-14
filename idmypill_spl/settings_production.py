from .settings import *

DEBUG = False

# configure database
if 'DATABASE_URL' in env:
    DATABASES = {
        'default': env.db()
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env('DJANGO_DATABASE_NAME', default='idmypill_spl'),
            'USER': env('DJANGO_DATABASE_USER', default='postgres'),
            'PASSWORD': env('DJANGO_DATABASE_PASSWORD', default='***'),
            'HOST': env('DJANGO_DATABASE_HOST', default='localhost'),
            'PORT': env('DJANGO_DATABASE_PORT', default='5432'),
        }
    }

# fix ssl mixed content issues
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Django security checklist settings.
# More details here: https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTP Strict Transport Security settings
# Without uncommenting the lines below, you will get security warnings when running ./manage.py check --deploy
# https://docs.djangoproject.com/en/3.2/ref/middleware/#http-strict-transport-security

# # Increase this number once you're confident everything works https://stackoverflow.com/a/49168623/8207
# SECURE_HSTS_SECONDS = 60
# # Uncomment these two lines if you are sure that you don't host any subdomains over HTTP.
# # You will get security warnings if you don't do this.
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

USE_HTTPS_IN_ABSOLUTE_URLS = True

# production hosts, supplied as a comma-separated DJANGO_ALLOWED_HOSTS env var
# (e.g. "api.yourdomain.com,www.yourdomain.com")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

RENDER_EXTERNAL_HOSTNAME = env('RENDER_EXTERNAL_HOSTNAME', default=None)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Turn on WhiteNoise storage backend that takes care of compressing static files
# and creating unique names for each version so they can safely be cached forever.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
