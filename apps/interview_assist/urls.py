"""
面试辅助模块URL配置。
"""
from django.urls import path
from .views import (
    SessionView,
    GenerateQuestionsView,
    RecordQAView,
    GenerateReportView,
)

app_name = 'interview_assist'

urlpatterns = [
    path('sessions/', SessionView.as_view(), name='session-create'),
    path('sessions/<uuid:session_id>/', SessionView.as_view(), name='session-detail'),
    path('sessions/<uuid:session_id>/questions/', GenerateQuestionsView.as_view(), name='generate-questions'),
    path('sessions/<uuid:session_id>/qa/', RecordQAView.as_view(), name='record-qa'),
    path('sessions/<uuid:session_id>/report/', GenerateReportView.as_view(), name='generate-report'),
]
