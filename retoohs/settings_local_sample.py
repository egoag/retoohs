import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
SECRET_KEY = '#q)ccsgnk86hc(wkc^vut8x68n!9ob8+6&5xf8n44t8&@^qm*j'

EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_PASSWORD = 'PASSWORD'
EMAIL_HOST_USER = 'postmaster@DOMAIN.com'
EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = '[retoohs]'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SENDER = 'admin@DOMAIN.com'

SITE_URL = 'https://retoohs.com'

DB_TYPE = 'sqlite'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')
ADMIN_URL = 'admins'
