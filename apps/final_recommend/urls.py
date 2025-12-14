"""
最终推荐模块URL配置。

目标路径: /api/recommend/
"""
from django.urls import path
from .views import ComprehensiveAnalysisView, RecommendStatsView

app_name = 'final_recommend'

urlpatterns = [
    # 统计接口
    path('stats/', RecommendStatsView.as_view(), name='stats'),
    # 综合分析 - GET获取候选人综合分析报告
    path('analysis/<uuid:resume_id>/', ComprehensiveAnalysisView.as_view(), name='analysis'),
]
