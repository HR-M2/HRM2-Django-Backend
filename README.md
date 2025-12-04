# 招聘管理系统后端 (Django Backend)

基于Django REST Framework构建的企业招聘管理系统后端API服务。

## 🏗️ 项目结构

```
Django-Backend/
├── config/                      # 项目配置
│   ├── settings/
│   │   ├── base.py             # 基础配置
│   │   ├── development.py      # 开发环境
│   │   ├── production.py       # 生产环境
│   │   └── testing.py          # 测试环境
│   ├── urls.py                  # 路由配置
│   ├── celery.py                # Celery配置
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                        # 应用模块
│   ├── common/                  # 公共模块
│   │   ├── response.py         # 统一响应格式
│   │   ├── exceptions.py       # 异常处理
│   │   ├── pagination.py       # 分页
│   │   ├── mixins.py           # 视图Mixins
│   │   └── utils.py            # 工具函数
│   │
│   ├── position_settings/       # 岗位设置模块
│   ├── resume_screening/        # 简历初筛模块
│   │   ├── views/              # 拆分的视图
│   │   ├── services/           # 服务层
│   │   └── tasks.py            # Celery任务
│   │
│   ├── video_analysis/          # 视频分析模块
│   ├── interview_assist/        # 面试辅助模块
│   └── final_recommend/         # 最终推荐模块
│
├── services/                    # AI服务层
│   ├── llm/                     # LLM配置
│   │   └── config.py           # API配置(从环境变量读取)
│   └── agents/                  # Agent定义
│       ├── base.py             # 基础Agent管理
│       ├── screening_agents.py # 简历筛选Agent
│       └── evaluation_agents.py# 评估Agent
│
├── manage.py
├── requirements.txt
├── .env.example                 # 环境变量模板
└── .gitignore
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置以下关键项：
# - DJANGO_SECRET_KEY: Django密钥
# - LLM_API_KEY: AI模型API密钥
# - DB_PASSWORD: 数据库密码
```

### 3. 初始化数据库

```bash
# 生成迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 4. 运行开发服务器

```bash
# 开发模式
python manage.py runserver

# 指定端口
python manage.py runserver 8000
```

## 📡 API端点

### 岗位设置 `/api/v1/positions/`
- `GET /criteria/` - 获取招聘标准
- `POST /criteria/` - 更新招聘标准
- `GET /list/` - 获取岗位列表

### 简历筛选 `/api/v1/screening/`
- `POST /` - 提交筛选任务
- `GET /tasks/<task_id>/` - 查询任务状态
- `GET /tasks/` - 任务历史
- `GET /data/` - 简历数据列表
- `GET /groups/` - 简历组列表
- `POST /groups/create/` - 创建简历组
- `POST /link-video/` - 关联视频分析

### 视频分析 `/api/v1/video/`
- `POST /` - 上传视频
- `GET /list/` - 视频列表
- `GET /<video_id>/` - 查询分析状态
- `POST /<video_id>/update/` - 更新分析结果

### 面试辅助 `/api/v1/interview/`
- `POST /sessions/` - 创建会话
- `GET /sessions/<session_id>/` - 会话详情
- `POST /sessions/<session_id>/questions/` - 生成问题
- `POST /sessions/<session_id>/qa/` - 记录问答
- `POST /sessions/<session_id>/report/` - 生成报告

### 最终推荐 `/api/v1/recommend/`
- `POST /evaluation/` - 启动评估
- `GET /evaluation/<task_id>/` - 查询评估状态

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DJANGO_SECRET_KEY | Django密钥 | - |
| DJANGO_DEBUG | 调试模式 | True |
| DB_NAME | 数据库名 | recruitment_db |
| DB_USER | 数据库用户 | root |
| DB_PASSWORD | 数据库密码 | - |
| LLM_API_KEY | AI模型API密钥 | - |
| LLM_BASE_URL | AI服务地址 | https://api.siliconflow.cn/v1 |
| CELERY_BROKER_URL | Celery消息队列 | redis://localhost:6379/0 |

### 切换环境

```bash
# 开发环境 (默认)
export DJANGO_SETTINGS_MODULE=config.settings.development

# 生产环境
export DJANGO_SETTINGS_MODULE=config.settings.production

# 测试环境
export DJANGO_SETTINGS_MODULE=config.settings.testing
```

## 🧪 测试

```bash
# 运行所有测试
python manage.py test

# 运行特定模块测试
python manage.py test apps.resume_screening

# 使用pytest
pytest
```

## 📦 部署

### 使用Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 使用Docker

```dockerfile
# Dockerfile示例
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🔄 与原项目对比

### 改进点

| 改进项 | 原项目 | 新项目 |
|--------|--------|--------|
| API密钥管理 | 硬编码在源码中 | 环境变量管理 |
| 文件结构 | 单文件1000+行 | 按功能拆分 |
| 异步任务 | threading | Celery (可回退threading) |
| 响应格式 | 不统一 | 统一APIResponse |
| 异常处理 | 分散 | 集中管理 |
| 配置管理 | 单一settings | 环境分离 |
| 代码复用 | 大量重复 | 公共模块+Mixins |
| 测试 | 不完善 | 独立测试模块 |

## 📄 License

MIT License
