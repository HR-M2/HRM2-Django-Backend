# 确保Django启动时始终导入此应用
# 以便shared_task使用此应用
from .celery import app as celery_app

__all__ = ('celery_app',)
