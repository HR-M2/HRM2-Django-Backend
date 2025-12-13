# 面试辅助服务导出
# 数据库简化重构 - Phase 7: 添加 InterviewSessionService
from services.agents import InterviewAssistAgent, get_interview_assist_agent

# InterviewSessionService 在 apps.interview_assist.services 模块 (services.py) 中定义
# 由于 Python 包优先于模块，需要直接导入文件
import importlib.util
import os

# 动态导入 services.py 文件
_services_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services.py')
if os.path.exists(_services_file):
    _spec = importlib.util.spec_from_file_location("interview_session_service", _services_file)
    _module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    InterviewSessionService = _module.InterviewSessionService
else:
    InterviewSessionService = None

__all__ = [
    'InterviewAssistAgent',
    'get_interview_assist_agent',
    'InterviewSessionService',
]
