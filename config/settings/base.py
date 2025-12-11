"""
招聘系统API项目的Django基础配置。
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录路径，可通过 BASE_DIR / 'subdir' 方式引用子目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 将apps目录添加到Python路径
sys.path.insert(0, str(BASE_DIR / 'apps'))

# 安全警告：请在生产环境中使用安全的密钥！
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me-in-production')

# 应用定义
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.common',
    'apps.position_settings',
    'apps.resume_library',  # 简历库模块（独立）
    'apps.resume_screening',
    'apps.video_analysis',
    'apps.interview_assist',
    'apps.final_recommend',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.common.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 国际化设置
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件（CSS、JavaScript、图片）
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 媒体文件
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST框架配置
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.StandardPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'apps.common.exceptions.custom_exception_handler',
}

# drf-spectacular API文档配置
SPECTACULAR_SETTINGS = {
    'TITLE': 'HR招聘系统 API',
    'DESCRIPTION': '''
智能招聘管理系统后端API文档

## 功能模块
- **岗位设置** - 岗位标准管理、简历分配
- **简历筛选** - 简历上传与AI初筛
- **视频分析** - 面试视频分析（预留）
- **面试辅助** - AI面试问答助手
- **最终推荐** - 候选人综合评估
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    
    # Swagger UI 设置
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,  # 隐藏操作ID，更简洁
        'filter': True,  # 启用搜索过滤
        'docExpansion': 'list',  # 默认展开到列表级别
        'tagsSorter': 'alpha',  # 标签按字母排序
        'operationsSorter': 'method',  # 操作按方法排序
    },
    
    # 按URL路径自动分组标签
    'TAGS': [
        {'name': 'position-settings', 'description': '岗位设置 - 岗位标准管理与简历分配'},
        {'name': 'resume-screening', 'description': '简历筛选 - 简历上传与AI初筛分析'},
        {'name': 'video-analysis', 'description': '视频分析 - 面试视频分析（预留）'},
        {'name': 'interview-assist', 'description': '面试辅助 - AI面试问答助手'},
        {'name': 'final-recommend', 'description': '最终推荐 - 候选人综合评估分析'},
    ],
    
    # 钩子函数：过滤和自动分配标签
    'PREPROCESSING_HOOKS': ['config.spectacular_hooks.preprocess_exclude_path'],
    'POSTPROCESSING_HOOKS': ['config.spectacular_hooks.custom_postprocessing_hook'],
    
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
}

# CORS跨域配置
CORS_ALLOW_ALL_ORIGINS = True  # 生产环境中需要修改
CORS_ALLOW_CREDENTIALS = True

# Celery任务队列配置
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 如果日志目录不存在则创建
(BASE_DIR / 'logs').mkdir(exist_ok=True)
