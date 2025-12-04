"""
Admin configuration for resume screening module.
"""
from django.contrib import admin
from .models import ResumeScreeningTask, ScreeningReport, ResumeGroup, ResumeData


@admin.register(ResumeScreeningTask)
class ResumeScreeningTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'progress', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ScreeningReport)
class ScreeningReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'task', 'original_filename', 'created_at']
    list_filter = ['created_at']
    search_fields = ['original_filename']
    readonly_fields = ['id', 'created_at']


@admin.register(ResumeGroup)
class ResumeGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'group_name', 'position_title', 'resume_count', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['group_name', 'position_title']
    readonly_fields = ['id', 'created_at', 'updated_at', 'position_hash']


@admin.register(ResumeData)
class ResumeDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'candidate_name', 'position_title', 'created_at']
    list_filter = ['position_title', 'created_at']
    search_fields = ['candidate_name', 'position_title']
    readonly_fields = ['id', 'created_at', 'updated_at', 'resume_file_hash']
