"""
简历库模块URL配置。

目标路径: /api/library/
提供简历的上传、查询、删除等基础管理功能。
"""
from django.urls import path
from .views import (
    LibraryListView,
    LibraryDetailView,
    LibraryBatchDeleteView,
    LibraryCheckHashView,
)

app_name = 'resume_library'

urlpatterns = [
    # 简历列表和上传 - GET列表, POST上传
    path('', LibraryListView.as_view(), name='list'),
    
    # 简历详情 - GET/PUT/DELETE
    path('<uuid:id>/', LibraryDetailView.as_view(), name='detail'),
    
    # 批量删除 - POST批量删除简历
    path('batch-delete/', LibraryBatchDeleteView.as_view(), name='batch-delete'),
    
    # 检查哈希 - POST检查文件是否已存在
    path('check-hash/', LibraryCheckHashView.as_view(), name='check-hash'),
]
