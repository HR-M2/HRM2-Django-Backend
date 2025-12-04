"""
Django开发环境配置。
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# 数据库 - 开发环境使用SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS - 开发环境允许所有来源
CORS_ALLOW_ALL_ORIGINS = True

# 开发环境禁用CSRF以便API测试
MIDDLEWARE = [m for m in MIDDLEWARE if 'csrf' not in m.lower()]

# 开发环境邮件后端
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 调试工具栏（可选）
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass
