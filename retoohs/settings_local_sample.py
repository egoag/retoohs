import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
SECRET_KEY = '#q)ccsgnk86hc(wkc^vut8x68n!9ob8+6&5xf8n44t8&@^qm*j'
DB_TYPE = 'sqlite'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
ADMIN_URL = 'admins'
