"""
岗位设置模块URL配置 - 支持多岗位CRUD和简历分配。
"""
from django.urls import path
from .views import (
    RecruitmentCriteriaView, 
    PositionCriteriaListView,
    PositionCriteriaDetailView,
    PositionAssignResumesView,
    PositionRemoveResumeView
)

app_name = 'position_settings'

urlpatterns = [
    # 原版路径 - 保持向后兼容（获取/更新默认岗位）
    path('', RecruitmentCriteriaView.as_view(), name='criteria'),
    
    # 多岗位管理 API
    path('positions/', PositionCriteriaListView.as_view(), name='positions-list'),
    path('positions/<uuid:position_id>/', PositionCriteriaDetailView.as_view(), name='position-detail'),
    
    # 简历分配 API
    path('positions/<uuid:position_id>/assign-resumes/', PositionAssignResumesView.as_view(), name='assign-resumes'),
    path('positions/<uuid:position_id>/remove-resume/<uuid:resume_id>/', PositionRemoveResumeView.as_view(), name='remove-resume'),
    
    # 保留旧的列表接口（向后兼容）
    path('list/', PositionCriteriaListView.as_view(), name='list'),
]
