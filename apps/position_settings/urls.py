"""
岗位设置模块URL配置。

目标路径: /api/positions/
支持岗位CRUD、简历分配和AI生成功能。
"""
from django.urls import path
from .views import (
    PositionListView,
    PositionDetailView,
    PositionAssignResumesView,
    PositionRemoveResumeView,
    PositionAIGenerateView
)

app_name = 'position_settings'

urlpatterns = [
    # 岗位列表和创建 - GET列表, POST创建
    path('', PositionListView.as_view(), name='list'),
    
    # 岗位详情 - GET/PUT/DELETE
    path('<uuid:position_id>/', PositionDetailView.as_view(), name='detail'),
    
    # 简历分配 - POST分配简历到岗位
    path('<uuid:position_id>/resumes/', PositionAssignResumesView.as_view(), name='resumes'),
    
    # 移除简历 - DELETE从岗位移除指定简历
    path('<uuid:position_id>/resumes/<uuid:resume_id>/', PositionRemoveResumeView.as_view(), name='remove-resume'),
    
    # AI生成 - POST根据描述生成岗位要求
    path('ai/generate/', PositionAIGenerateView.as_view(), name='ai-generate'),
]
