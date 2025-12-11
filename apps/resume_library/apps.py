"""
简历库应用配置。
"""
from django.apps import AppConfig


class ResumeLibraryConfig(AppConfig):
    """简历库应用配置类。"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.resume_library'
    verbose_name = '简历库管理'
