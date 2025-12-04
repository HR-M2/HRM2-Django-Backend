"""
Admin configuration for interview assist module.
"""
from django.contrib import admin
from .models import InterviewAssistSession, InterviewQARecord


@admin.register(InterviewAssistSession)
class InterviewAssistSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_candidate_name', 'interviewer_name', 'status', 'current_round', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['interviewer_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_candidate_name(self, obj):
        return obj.resume_data.candidate_name if obj.resume_data else ''
    get_candidate_name.short_description = '候选人'


@admin.register(InterviewQARecord)
class InterviewQARecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'round_number', 'question_category', 'was_followed_up', 'created_at']
    list_filter = ['question_category', 'was_followed_up', 'created_at']
    readonly_fields = ['id', 'created_at']
