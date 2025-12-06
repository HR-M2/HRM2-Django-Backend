"""
Admin configuration for interview assist module.
"""
from django.contrib import admin
from .models import InterviewAssistSession


@admin.register(InterviewAssistSession)
class InterviewAssistSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_candidate_name', 'get_qa_count', 'is_completed', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def get_candidate_name(self, obj):
        return obj.resume_data.candidate_name if obj.resume_data else ''
    get_candidate_name.short_description = '候选人'
    
    def get_qa_count(self, obj):
        return obj.current_round
    get_qa_count.short_description = '问答轮数'
