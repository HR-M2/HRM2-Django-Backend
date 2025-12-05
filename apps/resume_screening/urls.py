"""
简历筛选模块URL配置 - 与原版 RecruitmentSystemAPI 保持一致。
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
    # 筛选 - 原版路径: screening/
    path('screening/', ResumeScreeningView.as_view(), name='screening'),
    
    # 任务状态 - 原版路径: tasks/<uuid:task_id>/status/
    path('tasks/<uuid:task_id>/status/', ScreeningTaskStatusView.as_view(), name='task-status'),
    
    # 历史任务 - 原版路径: tasks-history/
    path('tasks-history/', TaskHistoryView.as_view(), name='task-history'),
    
    # 报告下载 - 原版路径: reports/<uuid:report_id>/download/
    path('reports/<uuid:report_id>/download/', ReportDownloadView.as_view(), name='report-download'),
    
    # 报告详情 - 原版路径: reports/<uuid:report_id>/detail/
    path('reports/<uuid:report_id>/detail/', ResumeDataDetailView.as_view(), name='report-detail'),
    
    # 简历数据
    path('data/', ResumeDataView.as_view(), name='resume-data'),
    
    # 简历组 - 与原版路径一致
    path('groups/create/', CreateResumeGroupView.as_view(), name='group-create'),
    path('groups/add-resume/', AddResumeToGroupView.as_view(), name='group-add-resume'),
    path('groups/remove-resume/', RemoveResumeFromGroupView.as_view(), name='group-remove-resume'),
    path('groups/set-status/', SetGroupStatusView.as_view(), name='group-set-status'),
    path('groups/<uuid:group_id>/', ResumeGroupDetailView.as_view(), name='group-detail'),
    path('groups/', ResumeGroupListView.as_view(), name='group-list'),
    
    # 视频关联 - 原版路径
    path('link-resume-to-video/', LinkResumeVideoView.as_view(), name='link-video'),
    path('unlink-resume-from-video/', UnlinkResumeVideoView.as_view(), name='unlink-video'),
]
