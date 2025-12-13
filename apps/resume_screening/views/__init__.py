from .screening import ResumeScreeningView, ScreeningTaskStatusView
from .resume_data import ResumeDataDetailView
from .task import TaskHistoryView, TaskDeleteView, ReportDownloadView
from .link import LinkResumeVideoView, UnlinkResumeVideoView
from .dev_tools import GenerateRandomResumesView

# 注意：简历库视图已合并到 apps.resume 模块（Phase 5 实现）
# 原 resume_library 应用已废弃

__all__ = [
    'ResumeScreeningView',
    'ScreeningTaskStatusView',
    'ResumeDataDetailView',
    'TaskHistoryView',
    'TaskDeleteView',
    'ReportDownloadView',
    'LinkResumeVideoView',
    'UnlinkResumeVideoView',
    # 开发测试工具
    'GenerateRandomResumesView',
]
