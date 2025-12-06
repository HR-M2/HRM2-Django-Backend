# 保留旧的导入路径以保持向后兼容
# 但推荐使用 from services.agents import InterviewAssistAgent
from .interview_assistant import InterviewAssistant

# 同时导出新的Agent类，方便迁移
from services.agents import InterviewAssistAgent, get_interview_assist_agent

__all__ = [
    'InterviewAssistant',  # 旧版（模拟实现），将被废弃
    'InterviewAssistAgent',  # 新版（LLM实现）
    'get_interview_assist_agent',
]
