"""
简历库管理后台配置。
"""
from django.contrib import admin
from .models import ResumeLibrary


@admin.register(ResumeLibrary)
class ResumeLibraryAdmin(admin.ModelAdmin):
    """简历库管理后台。"""
    
    list_display = [
        'id', 'filename', 'candidate_name', 
        'is_screened', 'is_assigned', 'created_at'
    ]
    list_filter = ['is_screened', 'is_assigned', 'created_at']
    search_fields = ['filename', 'candidate_name', 'content']
    readonly_fields = ['id', 'file_hash', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'filename', 'candidate_name')
        }),
        ('文件信息', {
            'fields': ('file_hash', 'file_size', 'file_type')
        }),
        ('内容', {
            'fields': ('content', 'notes'),
            'classes': ('collapse',)
        }),
        ('状态', {
            'fields': ('is_screened', 'is_assigned')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at')
        }),
    )
