"""
Admin configuration for final recommendation module.
"""
from django.contrib import admin
from .models import InterviewEvaluationTask


@admin.register(InterviewEvaluationTask)
class InterviewEvaluationTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'group_id', 'status', 'progress', 'current_speaker', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['group_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
