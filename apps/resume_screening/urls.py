"""
简历筛选模块URL配置。

目标路径: /api/screening/
注意：简历库相关API已迁移到 apps.resume_library 模块（/api/library/）
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
    TaskDeleteView,
    ReportDownloadView,
    LinkResumeVideoView,
    UnlinkResumeVideoView,
    GenerateRandomResumesView,
    ForceScreeningErrorView,
    ResetScreeningTestStateView,
)

app_name = 'resume_screening'

urlpatterns = [
    # 提交筛选 - POST提交筛选任务
    path('', ResumeScreeningView.as_view(), name='submit'),
    
    # 任务列表 - GET获取历史任务
    path('tasks/', TaskHistoryView.as_view(), name='task-list'),
    
    # 任务详情 - GET获取状态, DELETE删除任务
    path('tasks/<uuid:task_id>/', TaskDeleteView.as_view(), name='task-detail'),
    
    # 任务状态 - GET获取任务实时状态
    path('tasks/<uuid:task_id>/status/', ScreeningTaskStatusView.as_view(), name='task-status'),
    
    # 报告 - GET获取报告详情
    path('reports/<uuid:report_id>/', ResumeDataDetailView.as_view(), name='report'),
    
    # 报告下载 - GET下载报告文件
    path('reports/<uuid:report_id>/download/', ReportDownloadView.as_view(), name='report-download'),
    
    # 简历数据 - GET获取筛选后的简历数据
    path('data/', ResumeDataView.as_view(), name='data'),
    
    # 简历组 - GET列表, POST创建
    path('groups/', ResumeGroupListView.as_view(), name='group-list'),
    path('groups/create/', CreateResumeGroupView.as_view(), name='group-create'),
    
    # 简历组详情 - GET/DELETE
    path('groups/<uuid:group_id>/', ResumeGroupDetailView.as_view(), name='group-detail'),
    
    # 简历组操作
    path('groups/add-resume/', AddResumeToGroupView.as_view(), name='group-add-resume'),
    path('groups/remove-resume/', RemoveResumeFromGroupView.as_view(), name='group-remove-resume'),
    path('groups/set-status/', SetGroupStatusView.as_view(), name='group-set-status'),
    
    # 视频关联
    path('videos/link/', LinkResumeVideoView.as_view(), name='video-link'),
    path('videos/unlink/', UnlinkResumeVideoView.as_view(), name='video-unlink'),
    
    # 开发测试工具
    path('dev/generate-resumes/', GenerateRandomResumesView.as_view(), name='dev-generate'),
    path('dev/force-error/', ForceScreeningErrorView.as_view(), name='dev-force-error'),
    path('dev/reset-state/', ResetScreeningTestStateView.as_view(), name='dev-reset-state'),
]
