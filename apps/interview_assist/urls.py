"""
面试辅助模块URL配置。

目标路径: /api/interviews/
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
    # 会话列表和创建 - GET列表, POST创建
    path('sessions/', SessionView.as_view(), name='session-list'),
    
    # 会话详情 - GET/PUT/DELETE
    path('sessions/<uuid:session_id>/', SessionView.as_view(), name='session-detail'),
    
    # 生成问题 - POST生成面试问题
    path('sessions/<uuid:session_id>/questions/', GenerateQuestionsView.as_view(), name='questions'),
    
    # 记录问答 - POST记录面试问答
    path('sessions/<uuid:session_id>/qa/', RecordQAView.as_view(), name='qa'),
    
    # 生成报告 - POST生成面试报告
    path('sessions/<uuid:session_id>/report/', GenerateReportView.as_view(), name='report'),
]
