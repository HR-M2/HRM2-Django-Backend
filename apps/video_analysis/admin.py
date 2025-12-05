"""
Admin configuration for video analysis module.
"""
from django.contrib import admin
from .models import VideoAnalysis


@admin.register(VideoAnalysis)
class VideoAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'candidate_name', 'position_applied', 'status', 'confidence_score', 'created_at']
    list_filter = ['status', 'position_applied', 'created_at']
    search_fields = ['candidate_name', 'position_applied', 'video_name']
    readonly_fields = ['id', 'created_at']
