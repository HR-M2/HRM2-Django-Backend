from .screening import ResumeScreeningView, ScreeningTaskStatusView
from .resume_data import ResumeDataView, ResumeDataDetailView
from .resume_group import (
    ResumeGroupListView, 
    ResumeGroupDetailView,
    CreateResumeGroupView,
    AddResumeToGroupView,
    RemoveResumeFromGroupView,
    SetGroupStatusView
)
from .task import TaskHistoryView, ReportDownloadView
from .link import LinkResumeVideoView, UnlinkResumeVideoView

__all__ = [
    'ResumeScreeningView',
    'ScreeningTaskStatusView',
    'ResumeDataView',
    'ResumeDataDetailView',
    'ResumeGroupListView',
    'ResumeGroupDetailView',
    'CreateResumeGroupView',
    'AddResumeToGroupView',
    'RemoveResumeFromGroupView',
    'SetGroupStatusView',
    'TaskHistoryView',
    'ReportDownloadView',
    'LinkResumeVideoView',
    'UnlinkResumeVideoView',
]
