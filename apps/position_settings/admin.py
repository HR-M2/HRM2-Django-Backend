"""
Admin configuration for position settings module.
"""
from django.contrib import admin
from .models import PositionCriteria


@admin.register(PositionCriteria)
class PositionCriteriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'position', 'department', 'min_experience', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['position', 'department']
    readonly_fields = ['id', 'created_at', 'updated_at']
