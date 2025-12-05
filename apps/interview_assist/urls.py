"""
面试辅助模块URL配置 - 与原版 RecruitmentSystemAPI 保持一致。
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
    # 会话管理 - 原版路径
    path('sessions/', SessionView.as_view(), name='session-create'),
    path('sessions/<uuid:session_id>/', SessionView.as_view(), name='session-detail'),
    
    # 问题生成 - 原版路径: generate-questions/
    path('sessions/<uuid:session_id>/generate-questions/', GenerateQuestionsView.as_view(), name='generate-questions'),
    
    # 记录问答 - 原版路径: record-qa/
    path('sessions/<uuid:session_id>/record-qa/', RecordQAView.as_view(), name='record-qa'),
    
    # 生成报告 - 原版路径: generate-report/
    path('sessions/<uuid:session_id>/generate-report/', GenerateReportView.as_view(), name='generate-report'),
]
