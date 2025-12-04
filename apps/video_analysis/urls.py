"""
视频分析模块URL配置。
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
    path('', VideoAnalysisView.as_view(), name='upload'),
    path('list/', VideoAnalysisListView.as_view(), name='list'),
    path('<uuid:video_id>/', VideoAnalysisStatusView.as_view(), name='status'),
    path('<uuid:video_id>/update/', VideoAnalysisUpdateView.as_view(), name='update'),
]
