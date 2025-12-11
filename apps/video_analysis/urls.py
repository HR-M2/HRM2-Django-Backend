"""
视频分析模块URL配置。

目标路径: /api/videos/
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
    # 视频列表和上传 - GET列表, POST上传
    path('', VideoAnalysisListView.as_view(), name='list'),
    
    # 上传视频 - POST上传新视频
    path('upload/', VideoAnalysisView.as_view(), name='upload'),
    
    # 视频状态 - GET获取分析状态
    path('<uuid:video_id>/status/', VideoAnalysisStatusView.as_view(), name='status'),
    
    # 更新视频 - PUT更新视频信息
    path('<uuid:video_id>/', VideoAnalysisUpdateView.as_view(), name='detail'),
]
