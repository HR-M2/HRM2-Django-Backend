"""
WSGI config for recruitment_api project.
"""
import os
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

# 加载 .env 文件
load_dotenv()

# 根据 DJANGO_ENV 环境变量选择配置，默认使用开发环境
env = os.getenv('DJANGO_ENV', 'development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{env}')

application = get_wsgi_application()
