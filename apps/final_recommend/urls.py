"""
最终推荐模块URL配置 - 与原版 RecruitmentSystemAPI 保持一致。
"""
from django.urls import path
from .views import InterviewEvaluationView, ReportDownloadView, CandidateComprehensiveAnalysisView

app_name = 'final_recommend'

urlpatterns = [
    # 原版路径
    path('interview-evaluation/', InterviewEvaluationView.as_view(), name='evaluation'),
    path('interview-evaluation/<uuid:task_id>/', InterviewEvaluationView.as_view(), name='evaluation-detail'),
    path('interview-evaluation/<uuid:task_id>/delete/', InterviewEvaluationView.as_view(), name='evaluation-delete'),
    path('download-report/<path:file_path>', ReportDownloadView.as_view(), name='download'),
    
    # 新版单人综合分析
    path('comprehensive-analysis/<uuid:resume_id>/', CandidateComprehensiveAnalysisView.as_view(), name='comprehensive-analysis'),
]
