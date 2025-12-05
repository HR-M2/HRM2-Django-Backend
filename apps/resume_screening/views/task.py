"""
任务管理视图模块 - 与原版 RecruitmentSystemAPI 返回格式保持一致。
"""
import logging
from django.http import FileResponse, JsonResponse

from apps.common.mixins import SafeAPIView
from apps.common.pagination import paginate_queryset

from ..models import ResumeScreeningTask, ScreeningReport, ResumeData

logger = logging.getLogger(__name__)


class TaskHistoryView(SafeAPIView):
    """
    任务历史API
    GET: 获取历史任务列表
    DELETE: 删除指定任务
    """
    
    def handle_get(self, request):
        """获取任务历史，支持分页。"""
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 50)
        status_filter = request.GET.get('status')
        
        queryset = ResumeScreeningTask.objects.all().order_by('-created_at')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        tasks = queryset[start:end]
        
        result = []
        for task in tasks:
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
        
        # 返回与原版一致的格式
        return JsonResponse({
            "tasks": result,
            "total": total,
            "page": page,
            "page_size": page_size
        })
    
    def _get_reports(self, task):
        """获取任务的报告。"""
        reports = ScreeningReport.objects.filter(task=task)
        result = []
        
        for report in reports:
            report_data = {
                "report_id": str(report.id),
                "report_filename": report.original_filename,
                "download_url": f"/resume-screening/reports/{report.id}/download/",
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


class TaskDeleteView(SafeAPIView):
    """
    删除任务API
    DELETE: 删除指定任务
    """
    
    def handle_delete(self, request, task_id):
        """删除指定任务及其关联数据。"""
        task = self.get_object_or_404(ResumeScreeningTask, id=task_id)
        
        # 删除关联的报告和简历数据（级联删除会自动处理）
        task_id_str = str(task.id)
        task.delete()
        
        logger.info(f"Deleted task {task_id_str}")
        
        return JsonResponse({
            "message": "任务删除成功",
            "task_id": task_id_str
        })


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
