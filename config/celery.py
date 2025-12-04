"""
招聘系统API项目的Celery配置。
"""
import os
from celery import Celery

# 为Celery程序设置默认的Django配置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('recruitment_api')

# 使用字符串表示worker不需要将配置对象序列化到子进程
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有已注册的Django应用配置中加载任务模块
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
