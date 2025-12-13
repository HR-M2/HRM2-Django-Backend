"""
Admin configuration for resume screening module.

数据库简化重构：删除废弃模型的 admin 注册
"""
from django.contrib import admin
from .models import ScreeningTask


@admin.register(ScreeningTask)
class ScreeningTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'position', 'status', 'progress', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id']
    readonly_fields = ['id', 'created_at']
