"""
简历筛选模块URL配置。

目标路径: /api/screening/
注意：简历库相关API已迁移到 apps.resume 模块（/api/resumes/）
"""
from django.urls import path
from .views import (
    ScreeningSubmitView,
    ScreeningTaskStatusView,
    ScreeningReportView,
    TaskHistoryView,
    TaskDeleteView,
    ReportDownloadView,
    LinkResumeVideoView,
    UnlinkResumeVideoView,
    GenerateRandomResumesView,
)

app_name = 'resume_screening'

urlpatterns = [
    # 提交筛选 - POST提交筛选任务
    path('', ScreeningSubmitView.as_view(), name='submit'),
    
    # 任务列表 - GET获取历史任务
    path('tasks/', TaskHistoryView.as_view(), name='task-list'),
    
    # 任务详情 - GET获取状态, DELETE删除任务
    path('tasks/<uuid:task_id>/', TaskDeleteView.as_view(), name='task-detail'),
    
    # 任务状态 - GET获取任务实时状态
    path('tasks/<uuid:task_id>/status/', ScreeningTaskStatusView.as_view(), name='task-status'),
    
    # 报告 - GET获取报告详情
    path('reports/<uuid:report_id>/', ScreeningReportView.as_view(), name='report'),
    
    # 报告下载 - GET下载报告文件
    path('reports/<uuid:report_id>/download/', ReportDownloadView.as_view(), name='report-download'),
    
    # 视频关联
    path('videos/link/', LinkResumeVideoView.as_view(), name='video-link'),
    path('videos/unlink/', UnlinkResumeVideoView.as_view(), name='video-unlink'),
    
    # 开发测试工具
    path('dev/generate-resumes/', GenerateRandomResumesView.as_view(), name='dev-generate'),
]
