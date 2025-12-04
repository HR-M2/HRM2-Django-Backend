"""
Django测试环境配置。
"""
from .base import *

DEBUG = False

# 使用内存SQLite以加快测试速度
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 使用更快的密码哈希器进行测试
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 测试期间禁用日志
LOGGING = {}

# 测试环境Celery配置
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
