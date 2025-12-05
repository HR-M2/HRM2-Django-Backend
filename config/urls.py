"""
招聘系统API项目URL配置。
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),
    
    # API端点 - 与原版 RecruitmentSystemAPI 保持一致
    path('position-settings/', include('apps.position_settings.urls')),
    path('resume-screening/', include('apps.resume_screening.urls')),
    path('video-analysis/', include('apps.video_analysis.urls')),
    path('final-recommend/', include('apps.final_recommend.urls')),
    path('interview-assist/', include('apps.interview_assist.urls')),
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
