"""
最终推荐模块URL配置。

目标路径: /api/recommend/
"""
from django.urls import path
from .views import CandidateComprehensiveAnalysisView

app_name = 'final_recommend'

urlpatterns = [
    # 综合分析 - GET获取候选人综合分析报告
    path('analysis/<uuid:resume_id>/', CandidateComprehensiveAnalysisView.as_view(), name='analysis'),
]
