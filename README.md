# HRM2-Django-Backend

企业招聘管理系统（HRM2）的 Django REST Framework 后端，整合岗位管理、简历筛选、面试辅助、视频分析与最终推荐等招聘流程。配套 AI Agent 服务、可插拔任务队列与完善的开发/部署工具链。

## ✨ 核心特性

1. **模块化多应用架构**：岗位、筛选、视频、面试、推荐等模块独立又互通。
2. **AI 能力内置**：`services/agents` 中封装多种 LLM Agent（岗位 JD 生成、筛选评估、面试辅助等）。
3. **全链路自动化**：使用 threading 实现异步任务处理。
4. **一键启动器**：`run.py` 提供环境检查、迁移与运行一站式体验。
5. **覆蓋测试**：独立 `tests/` 目录与 `pytest` + `pytest-django` 配置，便于持续集成。

## 🧰 技术栈

| 层级 | 技术 |
| ---- | ---- |
| 语言 | Python 3.11 |
| Web 框架 | Django 5 + Django REST Framework |
| 异步处理 | Python threading |
| 数据库 | 默认 SQLite（开发），可切换 MySQL / PostgreSQL |
| AI/LLM | pyautogen, OpenAI SDK，自定义 Agent 封装 |
| 其他 | django-cors-headers、channels (可选 WebSocket)、pytest/flake8/black/isort |

## 🏗️ 项目结构

```
HRM2-Django-Backend/
├── apps/
│   ├── common/              # SafeAPIView、统一异常/响应、分页、日志中间件
│   ├── position_settings/   # 岗位多维配置 & AI JD 生成
│   ├── resume_screening/    # 简历组、筛选任务、报告、简历库
│   ├── video_analysis/      # 视频上传、状态跟踪、结果同步
│   ├── interview_assist/    # AI 面试问答、记录、报告
│   └── final_recommend/     # 面试评估与结果下载
├── config/
│   ├── settings/
│   │   ├── base.py          # 基础配置（日志、REST、CORS 等）
│   │   ├── development.py   # 开发（SQLite + Debug Toolbar）
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py              # 五大模块 + admin 路由
│   ├── wsgi.py / asgi.py
├── services/
│   └── agents/
│       ├── __init__.py          # Agent 导出
│       ├── base.py              # Base Agent 基类
│       ├── llm_config.py        # LLM 配置管理
│       ├── screening_agents.py  # 简历筛选 Agent
│       ├── evaluation_agents.py # 面试评估 Agent
│       ├── interview_assist_agent.py  # 面试辅助 Agent（问题生成、问答记录、报告）
│       ├── position_ai_service.py     # 岗位 AI 生成服务
│       └── dev_tools_service.py       # 开发测试工具服务（生成假简历等）
├── tests/
│   ├── conftest.py          # pytest 夹具配置
│   ├── test_resume_screening.py
│   └── test_video_analysis.py
├── Docs/
│   ├── API分析报告.md       # API 分析文档
│   └── 分析API.py           # API 分析脚本
├── run.py                   # 一键启动器（参数：env/port/host/migrate-only 等）
├── manage.py
├── requirements.txt         # 后端依赖
├── .env.example             # 环境变量模板
├── pytest.ini
├── data/ | media/ | logs/   # 数据、上传、日志输出
└── README.md
```

## ⚙️ 环境要求

- Python 3.11+
- pip / virtualenv
- MySQL 或 PostgreSQL（生产环境推荐，开发默认 SQLite）

## 🚀 快速开始

### 1. 一键启动（推荐）

```bash
# 默认：development + 127.0.0.1:8000
python run.py

# 自定义
python run.py -p 8080                # 指定端口
python run.py -e prod                # 使用生产配置
python run.py --host 0.0.0.0         # 允许外网访问
python run.py --skip-checks          # 跳过依赖/迁移检查
python run.py --migrate-only         # 仅执行迁移
python run.py -h                     # 查看全部参数
```

### 2. 手动启动

1. **创建虚拟环境并安装依赖**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   # macOS / Linux
   cp .env.example .env
   # Windows
   copy .env.example .env
   ```
   - 填写 `DJANGO_SECRET_KEY`、数据库凭据以及 `LLM_API_KEY`
   - `development.py` 默认使用 SQLite，无需额外 DB 设置

3. **数据库迁移与管理账号**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser    # 可选
   ```

4. **启动 Django 服务**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## 🔑 环境变量（.env.example）

| 变量 | 说明 | 默认值 |
| ---- | ---- | ---- |
| `DJANGO_SECRET_KEY` | Django 密钥 | 必填 |
| `DJANGO_DEBUG` | 调试开关 | `True` |
| `DJANGO_ALLOWED_HOSTS` | 允许的域名，逗号分隔 | `localhost,127.0.0.1` |
| `DB_ENGINE` | 数据库引擎 | `django.db.backends.mysql` |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | 数据库配置 | 见模板 |
| `LLM_MODEL` | 模型名称 | `deepseek-ai/DeepSeek-V3.2-Exp` |
| `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_TEMPERATURE` / `LLM_TIMEOUT` | LLM 调用配置 | 必填或默认 |
| `MEDIA_ROOT` / `STATIC_ROOT` | 文件存储目录 | `media` / `static` |

切换环境：

```bash
# 推荐：run.py 参数
python run.py -e dev|prod|test

# 或手动导出
export DJANGO_SETTINGS_MODULE=config.settings.development
```

## 🧩 功能模块概览

| 模块 | 说明 |
| ---- | ---- |
| `apps.position_settings` | 支持多岗位 CRUD、简历分配、AI JD 生成；兼容旧版接口。 |
| `apps.resume_screening` | 简历组管理、筛选任务、报告下载、简历库、开发测试工具 API。 |
| `apps.video_analysis` | 面试视频上传、状态查询、结果回写。 |
| `apps.interview_assist` | 面试会话管理、AI 生成问题（含兴趣点）、记录问答、生成候选提问、生成最终报告。 |
| `apps.final_recommend` | 单人综合分析、多维度评估（Rubric量表）、生成综合报告与录用建议。 |
| `services/agents` | 面向岗位/筛选/评估/面试辅助的 Agent 封装，统一 LLM 调用，支持可配置模型与温度。 |

## 📡 API 端点

### 岗位设置 `position-settings/`

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| GET/PUT | `/` | 获取 / 更新默认岗位配置（向后兼容原接口） |
| GET/POST | `/positions/` | 岗位列表 / 新增岗位 |
| GET/PATCH/DELETE | `/positions/<uuid:position_id>/` | 岗位详情维护 |
| POST | `/positions/<uuid:position_id>/assign-resumes/` | 分配简历到岗位 |
| DELETE | `/positions/<uuid:position_id>/remove-resume/<uuid:resume_id>/` | 从岗位移除简历 |
| POST | `/ai/generate/` | 基于 JD 关键字 AI 生成岗位要求 |
| GET | `/list/` | 旧版岗位列表（兼容） |

### 简历筛选 `resume-screening/`

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| POST | `/screening/` | 创建筛选任务 |
| GET | `/tasks/<uuid:task_id>/status/` | 查询任务状态 |
| GET | `/tasks-history/` | 历史任务列表 |
| DELETE | `/tasks/<uuid:task_id>/` | 删除任务 |
| GET | `/reports/<uuid:report_id>/detail/` | 报告详情 |
| GET | `/reports/<uuid:report_id>/download/` | 下载报告 |
| GET | `/data/` | 简历数据列表 |
| GET | `/groups/` | 简历组列表 |
| GET | `/groups/<uuid:group_id>/` | 简历组详情 |
| POST | `/groups/create/` | 创建组 |
| POST | `/groups/add-resume/` | 添加简历到组 |
| POST | `/groups/remove-resume/` | 从组移除简历 |
| POST | `/groups/set-status/` | 更新组状态 |
| POST | `/link-resume-to-video/` | 关联简历与视频 |
| POST | `/unlink-resume-from-video/` | 取消关联 |
| GET/POST | `/library/` | 简历库列表 / 新增简历 |
| GET/PATCH/DELETE | `/library/<uuid:resume_id>/` | 简历库详情维护 |
| DELETE | `/library/batch-delete/` | 批量删除简历 |
| POST | `/library/check-hash/` | 去重校验 |
| POST | `/dev/generate-resumes/` | 开发测试生成假数据 |

### 视频分析 `video-analysis/`

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| POST | `/` | 上传视频并触发分析 |
| GET | `/list/` | 视频任务列表 |
| GET | `/<uuid:video_id>/status/` | 查询分析状态 |
| POST | `/<uuid:video_id>/update/` | 回写或修正分析结果 |

### 面试辅助 `interview-assist/`

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| POST | `/sessions/` | 创建会话 |
| GET | `/sessions/<uuid:session_id>/` | 会话详情（支持 ?resume_id= 按简历查询） |
| DELETE | `/sessions/<uuid:session_id>/` | 结束会话 |
| POST | `/sessions/<uuid:session_id>/generate-questions/` | 生成问答提纲 |
| POST | `/sessions/<uuid:session_id>/record-qa/` | 记录问答并生成候选提问 |
| POST | `/sessions/<uuid:session_id>/generate-report/` | 生成面试报告 |

### 最终推荐 `final-recommend/`

| 方法 | 路径 | 说明 |
| ---- | ---- | ---- |
| POST | `/interview-evaluation/` | 发起最终评估任务 |
| GET | `/interview-evaluation/<uuid:task_id>/` | 查询任务状态/结果 |
| DELETE | `/interview-evaluation/<uuid:task_id>/delete/` | 删除任务 |
| GET | `/download-report/<path:file_path>` | 下载评估报告 |
| POST | `/comprehensive-analysis/` | 单人综合分析（整合简历、初筛、面试数据） |
| GET | `/comprehensive-analysis/?resume_id=<uuid>` | 获取历史分析结果 |

> 统一入口 `config/urls.py` 还暴露 `/admin/`（Django Admin）与调试工具栏（开发环境）。

## 🧪 测试

```bash
# 运行全部 pytest（读取 pytest.ini）
pytest

# 只跑某个模块
pytest tests/test_resume_screening.py

# 使用 Django TestCase
python manage.py test apps.resume_screening
```

## 📦 部署

### Gunicorn

```bash
pip install -r requirements.txt
DJANGO_SETTINGS_MODULE=config.settings.production \
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Docker（示例）

```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🔄 与原项目 (RecruitmentSystemAPI) 对比

| 改进项 | 原项目 | 本项目 |
| ---- | ---- | ---- |
| API 密钥管理 | 硬编码 | .env + `python-dotenv` |
| 目录结构 | 单 app，逻辑耦合 | 多模块拆分 + services | 
| 异步任务 | threading | threading（简化实现） |
| 响应/异常 | 散落各处 | `apps.common` 封装 SafeAPIView、响应体统一 |
| 配置 | 单一 settings | dev/prod/test 分离，脚本化切换 |
| AI 能力 | 无 Agent 封装 | LLM Agent + 可配置模型 |
| 启动 | 手动繁琐 | `run.py` 检查 + 启动 + 迁移 |
| 测试 | 零散 | `tests/` + pytest + CI 友好 |

## 📄 License

MIT License

---

## 📝 更新日志

- **2025-12**: 新增 `interview_assist` 面试辅助模块，支持 AI 生成问题池、记录问答生成候选提问、最终报告生成
- **2025-12**: 新增 `dev_tools_service` 开发测试服务，支持批量生成模拟简历
- **2025-12**: `services/agents` 重构，新增 `interview_assist_agent.py` 面试辅助 Agent
- **2025-12**: 新增 `CandidateComprehensiveAnalyzer` 单人综合分析器，基于 Rubric 量表多维度评估
- **2025-12**: `final_recommend` 新增综合分析 API，支持保存与查询历史分析结果
- **2025-12**: `interview_assist` 支持按 resume_id 查询面试会话列表
