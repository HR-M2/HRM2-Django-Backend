# HRM2-Django-Backend

基于 Django REST Framework 构建的企业招聘管理系统后端 API 服务。

## 🏗️ 项目结构

```
HRM2-Django-Backend/
├── config/                      # 项目配置
│   ├── settings/
│   │   ├── base.py             # 基础配置
│   │   ├── development.py      # 开发环境
│   │   ├── production.py       # 生产环境
│   │   └── testing.py          # 测试环境
│   ├── urls.py                 # 路由配置
│   ├── celery.py               # Celery 配置
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                        # 应用模块
│   ├── common/                  # 公共模块
│   │   ├── mixins.py           # 视图基类 (SafeAPIView)
│   │   ├── exceptions.py       # 自定义异常
│   │   ├── pagination.py       # 分页工具
│   │   └── utils.py            # 工具函数
│   │
│   ├── position_settings/       # 岗位设置模块
│   ├── resume_screening/        # 简历筛选模块
│   │   ├── views/              # 视图 (按功能拆分)
│   │   ├── services/           # 业务服务层
│   │   └── tasks.py            # Celery 异步任务
│   │
│   ├── video_analysis/          # 视频分析模块
│   ├── interview_assist/        # 面试辅助模块
│   └── final_recommend/         # 最终推荐模块
│
├── services/                    # AI 服务层
│   ├── llm/                     # LLM 配置
│   │   └── config.py           # API 配置 (环境变量)
│   └── agents/                  # Agent 定义
│       ├── base.py             # 基础 Agent
│       ├── screening_agents.py # 筛选 Agent
│       └── evaluation_agents.py# 评估 Agent
│
├── run.py                       # 一键启动脚本
├── manage.py
├── requirements.txt
├── .env.example                 # 环境变量模板
└── .gitignore
```

## 🚀 快速开始

### 一键启动 (推荐)

```bash
# 默认启动 (开发环境, 8000 端口)
python run.py

# 指定端口
python run.py -p 8080

# 生产环境
python run.py -e prod

# 允许外部访问
python run.py --host 0.0.0.0

# 跳过检查快速启动
python run.py --skip-checks

# 查看更多选项
python run.py -h
```

### 手动启动

#### 1. 环境准备

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

#### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置关键项:
# - DJANGO_SECRET_KEY: Django 密钥
# - LLM_API_KEY: AI 模型 API 密钥
# - DB_PASSWORD: 数据库密码 (使用 MySQL 时)
```

#### 3. 初始化数据库

```bash
python manage.py migrate
python manage.py createsuperuser  # 可选
```

#### 4. 启动服务器

```bash
python manage.py runserver 8000
```

## 📡 API 端点

### 岗位设置 `/position-settings/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/` | 获取/更新招聘标准 |
| GET | `/list/` | 获取岗位列表 |

### 简历筛选 `/resume-screening/`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/screening/` | 提交筛选任务 |
| GET | `/tasks/<task_id>/status/` | 查询任务状态 |
| GET | `/tasks-history/` | 任务历史列表 |
| GET | `/data/` | 简历数据列表 |
| GET | `/groups/` | 简历组列表 |
| GET | `/groups/<group_id>/` | 简历组详情 |
| POST | `/groups/create/` | 创建简历组 |
| POST | `/groups/add-resume/` | 添加简历到组 |
| POST | `/groups/remove-resume/` | 从组移除简历 |
| POST | `/groups/set-status/` | 设置组状态 |
| GET | `/reports/<report_id>/detail/` | 报告详情 |
| GET | `/reports/<report_id>/download/` | 下载报告 |
| POST | `/link-resume-to-video/` | 关联视频 |
| POST | `/unlink-resume-from-video/` | 取消关联 |

### 视频分析 `/video-analysis/`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/` | 上传视频 |
| GET | `/list/` | 视频列表 |
| GET | `/<video_id>/status/` | 查询分析状态 |
| POST | `/<video_id>/update/` | 更新分析结果 |

### 面试辅助 `/interview-assist/`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/sessions/` | 创建会话 |
| GET | `/sessions/<session_id>/` | 会话详情 |
| DELETE | `/sessions/<session_id>/` | 结束会话 |
| POST | `/sessions/<session_id>/generate-questions/` | 生成问题 |
| POST | `/sessions/<session_id>/record-qa/` | 记录问答 |
| POST | `/sessions/<session_id>/generate-report/` | 生成报告 |

### 最终推荐 `/final-recommend/`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/interview-evaluation/` | 启动评估任务 |
| GET | `/interview-evaluation/<task_id>/` | 查询评估状态 |
| DELETE | `/interview-evaluation/<task_id>/delete/` | 删除任务 |
| GET | `/download-report/<file_path>` | 下载评估报告 |

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DJANGO_SECRET_KEY` | Django 密钥 | - (必填) |
| `DJANGO_DEBUG` | 调试模式 | `True` |
| `DJANGO_ALLOWED_HOSTS` | 允许的域名 | `localhost,127.0.0.1` |
| `DB_ENGINE` | 数据库引擎 | `django.db.backends.mysql` |
| `DB_NAME` | 数据库名 | `recruitment_db` |
| `DB_USER` | 数据库用户 | `root` |
| `DB_PASSWORD` | 数据库密码 | - |
| `LLM_MODEL` | LLM 模型名 | `deepseek-ai/DeepSeek-V3.2-Exp` |
| `LLM_API_KEY` | AI 模型 API 密钥 | - (必填) |
| `LLM_BASE_URL` | AI 服务地址 | `https://api.siliconflow.cn/v1` |
| `LLM_TEMPERATURE` | 温度参数 | `0` |
| `LLM_TIMEOUT` | 超时时间 (秒) | `120` |
| `CELERY_BROKER_URL` | Celery 消息队列 | `redis://localhost:6379/0` |

### 切换环境

```bash
# 使用 run.py (推荐)
python run.py -e dev   # 开发环境
python run.py -e prod  # 生产环境
python run.py -e test  # 测试环境

# 手动设置
export DJANGO_SETTINGS_MODULE=config.settings.development
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定模块
pytest apps/resume_screening/

# 使用 Django 测试
python manage.py test apps.resume_screening
```

## 📦 部署

### 使用 Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 使用 Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🔄 与原项目 (RecruitmentSystemAPI) 对比

| 改进项 | 原项目 | 本项目 |
|--------|--------|--------|
| API 密钥管理 | 硬编码在源码 | 环境变量 (.env) |
| 文件结构 | 单文件 1000+ 行 | 按功能模块拆分 |
| 异步任务 | threading | Celery (可回退 threading) |
| 响应格式 | 不统一 | 统一使用 Response |
| 异常处理 | 分散各处 | SafeAPIView 集中处理 |
| 配置管理 | 单一 settings | 多环境分离 |
| 代码复用 | 大量重复 | 公共模块 + Mixins |
| 启动方式 | 手动多步 | run.py 一键启动 |
| 测试 | 不完善 | 独立测试模块 + pytest |

## 📄 License

MIT License
