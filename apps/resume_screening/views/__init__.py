from .screening import ResumeScreeningView, ScreeningTaskStatusView
from .resume_data import ResumeDataView, ResumeDataDetailView
from .task import TaskHistoryView, TaskDeleteView, ReportDownloadView
from .link import LinkResumeVideoView, UnlinkResumeVideoView
from .dev_tools import GenerateRandomResumesView, ForceScreeningErrorView, ResetScreeningTestStateView

# 向后兼容：简历库视图已迁移到 apps.resume_library 模块
# 保留重导出以支持现有代码
from apps.resume_library.views import (
    LibraryListView as ResumeLibraryListView,
    LibraryDetailView as ResumeLibraryDetailView,
    LibraryBatchDeleteView as ResumeLibraryBatchDeleteView,
    LibraryCheckHashView as ResumeLibraryCheckHashView,
)

__all__ = [
    'ResumeScreeningView',
    'ScreeningTaskStatusView',
    'ResumeDataView',
    'ResumeDataDetailView',
    'TaskHistoryView',
    'TaskDeleteView',
    'ReportDownloadView',
    'LinkResumeVideoView',
    'UnlinkResumeVideoView',
    # 简历库视图（已迁移到 apps.resume_library，此处为向后兼容）
    'ResumeLibraryListView',
    'ResumeLibraryDetailView',
    'ResumeLibraryBatchDeleteView',
    'ResumeLibraryCheckHashView',
    # 开发测试工具
    'GenerateRandomResumesView',
    'ForceScreeningErrorView',
    'ResetScreeningTestStateView',
]
