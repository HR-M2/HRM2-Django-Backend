"""
招聘系统API项目的Celery配置。
"""
import os
from dotenv import load_dotenv
from celery import Celery

# 加载 .env 文件
load_dotenv()

# 根据 DJANGO_ENV 环境变量选择配置，默认使用开发环境
env = os.getenv('DJANGO_ENV', 'development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{env}')

app = Celery('recruitment_api')

# 使用字符串表示worker不需要将配置对象序列化到子进程
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有已注册的Django应用配置中加载任务模块
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
