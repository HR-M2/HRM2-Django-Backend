"""
最终推荐模块URL配置。

注意: 批量评估相关路由（interview-evaluation, download-report）已废弃并移除。
"""
from django.urls import path
from .views import CandidateComprehensiveAnalysisView

app_name = 'final_recommend'

urlpatterns = [
    # 单人综合分析 API
    path('comprehensive-analysis/<uuid:resume_id>/', CandidateComprehensiveAnalysisView.as_view(), name='comprehensive-analysis'),
    
    # 已废弃的批量评估路由（已移除）:
    # - interview-evaluation/
    # - interview-evaluation/<uuid:task_id>/
    # - interview-evaluation/<uuid:task_id>/delete/
    # - download-report/<path:file_path>
]
