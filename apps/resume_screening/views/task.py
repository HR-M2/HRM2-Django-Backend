"""
任务管理视图模块。
"""
import logging
from django.http import FileResponse

from apps.common.mixins import SafeAPIView
from apps.common.response import APIResponse
from apps.common.pagination import paginate_queryset

from ..models import ResumeScreeningTask, ScreeningReport, ResumeData

logger = logging.getLogger(__name__)


class TaskHistoryView(SafeAPIView):
    """
    任务历史API
    GET: 获取历史任务列表
    """
    
    def handle_get(self, request):
        """获取任务历史，支持分页。"""
        status_filter = request.GET.get('status')
        
        queryset = ResumeScreeningTask.objects.all().order_by('-created_at')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        items, pagination = paginate_queryset(queryset, request)
        
        result = []
        for task in items:
            data = {
                "task_id": str(task.id),
                "status": task.status,
                "progress": task.progress,
                "current_step": task.current_step,
                "total_steps": task.total_steps,
                "created_at": task.created_at.isoformat()
            }
            
            if task.status == 'running' and task.current_speaker:
                data['current_speaker'] = task.current_speaker
            
            if task.status == 'completed':
                data['reports'] = self._get_reports(task)
                data['resume_data'] = self._get_resume_data(task)
            
            if task.status == 'failed' and task.error_message:
                data['error_message'] = task.error_message
            
            result.append(data)
        
        return APIResponse.paginated(result, pagination['total'], pagination['page'], pagination['page_size'])
    
    def _get_reports(self, task):
        """获取任务的报告。"""
        reports = ScreeningReport.objects.filter(task=task)
        result = []
        
        for report in reports:
            report_data = {
                "report_id": str(report.id),
                "report_filename": report.original_filename,
                "download_url": f"/api/v1/screening/reports/{report.id}/download/",
                "resume_content": report.resume_content or ""
            }
            
            if task.position_data:
                report_data["position_info"] = task.position_data
            
            result.append(report_data)
        
        return result
    
    def _get_resume_data(self, task):
        """获取任务的简历数据。"""
        resume_data_list = ResumeData.objects.filter(task=task)
        result = []
        
        for resume_data in resume_data_list:
            data = {
                "id": str(resume_data.id),
                "candidate_name": resume_data.candidate_name,
                "position_title": resume_data.position_title,
                "scores": resume_data.screening_score,
                "summary": resume_data.screening_summary,
                "json_content": resume_data.json_report_content,
                "resume_content": resume_data.resume_content,
                "report_md_url": resume_data.report_md_file.url if resume_data.report_md_file else None,
                "report_json_url": resume_data.report_json_file.url if resume_data.report_json_file else None,
            }
            
            if resume_data.video_analysis:
                data["video_analysis"] = {
                    "video_id": str(resume_data.video_analysis.id),
                    "video_name": resume_data.video_analysis.video_name,
                    "status": resume_data.video_analysis.status,
                    "confidence_score": resume_data.video_analysis.confidence_score,
                }
            
            result.append(data)
        
        return result


class ReportDownloadView(SafeAPIView):
    """
    报告下载API
    GET: 下载筛选报告
    """
    
    def handle_get(self, request, report_id):
        """下载筛选报告。"""
        report = self.get_object_or_404(ScreeningReport, id=report_id)
        
        response = FileResponse(
            report.md_file.open('rb'),
            content_type='text/markdown'
        )
        response['Content-Disposition'] = f'attachment; filename="{report.original_filename}"'
        
        return response
