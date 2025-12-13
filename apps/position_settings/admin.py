"""
Admin configuration for position settings module.

数据库简化重构：更新模型引用
"""
from django.contrib import admin
from .models import Position


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['title', 'department']
    readonly_fields = ['id', 'created_at', 'updated_at']
