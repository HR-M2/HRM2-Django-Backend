"""
招聘系统API项目URL配置。
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),
    
    # API文档
    path('api/', RedirectView.as_view(url='/api/docs/', permanent=False)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API端点 - 统一 /api/ 前缀
    path('api/positions/', include('apps.position_settings.urls')),
    # path('api/library/', ...) - 已合并到 resume 应用，待 Phase 6 创建 resume URLs
    path('api/screening/', include('apps.resume_screening.urls')),
    path('api/videos/', include('apps.video_analysis.urls')),
    path('api/recommend/', include('apps.final_recommend.urls')),
    path('api/interviews/', include('apps.interview_assist.urls')),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # 调试工具栏
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
