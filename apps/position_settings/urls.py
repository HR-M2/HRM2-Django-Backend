"""
岗位设置模块URL配置 - 与原版 RecruitmentSystemAPI 保持一致。
"""
from django.urls import path
from .views import RecruitmentCriteriaView, PositionCriteriaListView

app_name = 'position_settings'

urlpatterns = [
    # 原版路径: '' (空路径)
    path('', RecruitmentCriteriaView.as_view(), name='criteria'),
    # 额外的列表接口（新增功能，保留）
    path('list/', PositionCriteriaListView.as_view(), name='list'),
]
