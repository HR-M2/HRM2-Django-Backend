"""
最终推荐模块URL配置。
"""
from django.urls import path
from .views import InterviewEvaluationView, ReportDownloadView

app_name = 'final_recommend'

urlpatterns = [
    path('evaluation/', InterviewEvaluationView.as_view(), name='evaluation'),
    path('evaluation/<uuid:task_id>/', InterviewEvaluationView.as_view(), name='evaluation-detail'),
    path('download/<path:file_path>', ReportDownloadView.as_view(), name='download'),
]
