from .screening import ScreeningSubmitView, ScreeningTaskStatusView
from .resume_data import ScreeningReportView
from .task import TaskHistoryView, TaskDeleteView, ReportDownloadView
from .link import LinkResumeVideoView, UnlinkResumeVideoView
from .dev_tools import GenerateRandomResumesView

# 注意：简历库视图已合并到 apps.resume 模块（Phase 5 实现）
# 原 resume_library 应用已废弃

__all__ = [
    'ScreeningSubmitView',
    'ScreeningTaskStatusView',
    'ScreeningReportView',
    'TaskHistoryView',
    'TaskDeleteView',
    'ReportDownloadView',
    'LinkResumeVideoView',
    'UnlinkResumeVideoView',
    # 开发测试工具
    'GenerateRandomResumesView',
]
