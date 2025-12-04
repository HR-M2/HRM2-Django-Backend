"""
简历筛选模块URL配置。
"""
from django.urls import path
from .views import (
    ResumeScreeningView,
    ScreeningTaskStatusView,
    ResumeDataView,
    ResumeDataDetailView,
    ResumeGroupListView,
    ResumeGroupDetailView,
    CreateResumeGroupView,
    AddResumeToGroupView,
    RemoveResumeFromGroupView,
    SetGroupStatusView,
    TaskHistoryView,
    ReportDownloadView,
    LinkResumeVideoView,
    UnlinkResumeVideoView,
)

app_name = 'resume_screening'

urlpatterns = [
    # 筛选
    path('', ResumeScreeningView.as_view(), name='screening'),
    path('tasks/<uuid:task_id>/', ScreeningTaskStatusView.as_view(), name='task-status'),
    path('tasks/', TaskHistoryView.as_view(), name='task-history'),
    
    # 报告
    path('reports/<uuid:report_id>/download/', ReportDownloadView.as_view(), name='report-download'),
    path('reports/<uuid:resume_id>/', ResumeDataDetailView.as_view(), name='report-detail'),
    
    # 简历数据
    path('data/', ResumeDataView.as_view(), name='resume-data'),
    path('data/<uuid:resume_id>/', ResumeDataDetailView.as_view(), name='resume-data-detail'),
    
    # 简历组
    path('groups/', ResumeGroupListView.as_view(), name='group-list'),
    path('groups/create/', CreateResumeGroupView.as_view(), name='group-create'),
    path('groups/<uuid:group_id>/', ResumeGroupDetailView.as_view(), name='group-detail'),
    path('groups/add-resume/', AddResumeToGroupView.as_view(), name='group-add-resume'),
    path('groups/remove-resume/', RemoveResumeFromGroupView.as_view(), name='group-remove-resume'),
    path('groups/set-status/', SetGroupStatusView.as_view(), name='group-set-status'),
    
    # 视频关联
    path('link-video/', LinkResumeVideoView.as_view(), name='link-video'),
    path('unlink-video/', UnlinkResumeVideoView.as_view(), name='unlink-video'),
]
