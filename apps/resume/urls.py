"""
简历管理模块URL配置。

目标路径: /api/resumes/
合并原 /api/library/ 功能，提供简历CRUD、分配、筛选结果等API。
"""
from django.urls import path
from .views import (
    ResumeListView,
    ResumeDetailView,
    ResumeBatchDeleteView,
    ResumeCheckHashView,
    ResumeAssignView,
    ResumeScreeningResultView,
    ResumeStatsView,
)

app_name = 'resume'

urlpatterns = [
    # 简历列表和上传 - GET列表, POST批量上传
    path('', ResumeListView.as_view(), name='list'),
    
    # 简历统计 - GET获取统计数据
    path('stats/', ResumeStatsView.as_view(), name='stats'),
    
    # 批量删除 - POST批量删除简历
    path('batch-delete/', ResumeBatchDeleteView.as_view(), name='batch-delete'),
    
    # 检查哈希 - POST检查简历是否已存在
    path('check-hash/', ResumeCheckHashView.as_view(), name='check-hash'),
    
    # 分配简历 - POST批量分配简历到岗位
    path('assign/', ResumeAssignView.as_view(), name='assign'),
    
    # 简历详情 - GET/PUT/DELETE
    path('<uuid:resume_id>/', ResumeDetailView.as_view(), name='detail'),
    
    # 筛选结果 - GET/PUT
    path('<uuid:resume_id>/screening/', ResumeScreeningResultView.as_view(), name='screening-result'),
]
