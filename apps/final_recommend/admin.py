"""
Admin configuration for final recommendation module.

数据库简化重构：删除废弃模型的 admin 注册
"""
from django.contrib import admin
from .models import ComprehensiveAnalysis


@admin.register(ComprehensiveAnalysis)
class ComprehensiveAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'resume', 'final_score', 'recommendation_label', 'created_at']
    list_filter = ['created_at']
    search_fields = ['resume__candidate_name']
    readonly_fields = ['id', 'created_at']
