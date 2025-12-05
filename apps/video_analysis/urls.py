"""
视频分析模块URL配置 - 与原版 RecruitmentSystemAPI 保持一致。
"""
from django.urls import path
from .views import (
    VideoAnalysisView,
    VideoAnalysisStatusView,
    VideoAnalysisUpdateView,
    VideoAnalysisListView,
)

app_name = 'video_analysis'

urlpatterns = [
    # 原版路径
    path('', VideoAnalysisView.as_view(), name='upload'),
    path('<uuid:video_id>/status/', VideoAnalysisStatusView.as_view(), name='status'),
    path('<uuid:video_id>/update/', VideoAnalysisUpdateView.as_view(), name='update'),
    path('list/', VideoAnalysisListView.as_view(), name='list'),
]
