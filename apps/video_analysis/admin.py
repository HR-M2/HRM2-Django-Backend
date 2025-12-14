"""
Admin configuration for video analysis module.

数据库简化重构：更新字段引用
"""
from django.contrib import admin
from .models import VideoAnalysis


@admin.register(VideoAnalysis)
class VideoAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'resume', 'video_name', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['video_name', 'resume__candidate_name']
    readonly_fields = ['id', 'created_at']
