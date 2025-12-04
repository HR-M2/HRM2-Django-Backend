"""
岗位设置模块URL配置。
"""
from django.urls import path
from .views import RecruitmentCriteriaView, PositionCriteriaListView

app_name = 'position_settings'

urlpatterns = [
    path('criteria/', RecruitmentCriteriaView.as_view(), name='criteria'),
    path('list/', PositionCriteriaListView.as_view(), name='list'),
]
