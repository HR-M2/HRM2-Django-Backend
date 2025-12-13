"""
任务管理视图模块 - 与原版 RecruitmentSystemAPI 返回格式保持一致。

数据库简化重构：
- 使用 ScreeningTask 模型（原 ResumeScreeningTask 已重命名+简化）
- 使用 Resume 模型（原 ResumeData 已合并到 Resume）
- ScreeningReport 已删除（报告内容存入 Resume）
"""
import logging
from django.http import FileResponse

from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.pagination import paginate_queryset
from apps.common.schemas import (
    api_response, success_response,
    TaskListDataSerializer, IdResponseSerializer,
)

from ..models import ScreeningTask
from apps.resume.models import Resume

logger = logging.getLogger(__name__)


class TaskHistoryView(SafeAPIView):
    """
    任务历史API
    GET: 获取历史任务列表
    DELETE: 删除指定任务
    """
    
    @extend_schema(
        summary="获取任务历史列表",
        description="获取筛选任务历史列表，支持分页和状态过滤",
        parameters=[
            OpenApiParameter(name='page', type=int, description='页码'),
            OpenApiParameter(name='page_size', type=int, description='每页数量'),
            OpenApiParameter(name='status', type=str, description='状态过滤'),
        ],
        responses={200: api_response(TaskListDataSerializer(), "TaskHistory")},
        tags=["screening"],
    )
    def handle_get(self, request):
        """获取任务历史，支持分页。"""
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 50)
        status_filter = request.GET.get('status')
        
        queryset = ScreeningTask.objects.all().order_by('-created_at')
        
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
                "current_step": task.processed_count,
                "total_steps": task.total_count,
                "created_at": task.created_at.isoformat()
            }
            
            # 获取简历数据
            data['resume_data'] = self._get_resume_data(task)
            
            if task.status == 'failed' and task.error_message:
                data['error_message'] = task.error_message
            
            result.append(data)
        
        # 返回与原版一致的格式
        return ApiResponse.success(data={
            "tasks": result,
            "total": total,
            "page": page,
            "page_size": page_size
        })
    
    def _get_resume_data(self, task):
        """获取任务关联岗位的简历数据。"""
        # 通过 Position 关联获取简历
        resumes = Resume.objects.filter(position=task.position)
        result = []
        
        for resume in resumes:
            data = {
                "id": str(resume.id),
                "candidate_name": resume.candidate_name,
                "position_title": task.position.title,
                "screening_score": resume.screening_result.get('score') if resume.screening_result else None,
                "screening_summary": resume.screening_result.get('summary') if resume.screening_result else None,
                "resume_content": resume.content,
                "screening_report": resume.screening_report,
            }
            
            # 获取关联的视频分析
            video_analysis = resume.video_analyses.first()
            if video_analysis:
                data["video_analysis"] = {
                    "id": str(video_analysis.id),
                    "video_name": video_analysis.video_name,
                    "status": video_analysis.status,
                    "confidence_score": video_analysis.analysis_result.get('confidence_score') if video_analysis.analysis_result else None,
                }
            
            result.append(data)
        
        return result


class TaskDeleteView(SafeAPIView):
    """
    删除任务API
    DELETE: 删除指定任务
    """
    
    @extend_schema(
        summary="删除筛选任务",
        description="删除指定的筛选任务及其关联数据",
        responses={200: api_response(IdResponseSerializer(), "TaskDelete")},
        tags=["screening"],
    )
    def handle_delete(self, request, task_id):
        """删除指定任务及其关联数据。"""
        task = self.get_object_or_404(ScreeningTask, id=task_id)
        
        # 删除关联的报告和简历数据（级联删除会自动处理）
        task_id_str = str(task.id)
        task.delete()
        
        logger.info(f"Deleted task {task_id_str}")
        
        return ApiResponse.success(
            data={"task_id": task_id_str},
            message="任务删除成功"
        )


class ReportDownloadView(SafeAPIView):
    """
    报告下载API
    GET: 下载筛选报告
    
    支持两种方式：
    1. 如果有 md_file，直接返回文件
    2. 如果没有文件，从数据库的 ResumeData 动态生成 Markdown 报告
    """
    
    @extend_schema(
        summary="下载筛选报告",
        description="下载指定简历的筛选报告（Markdown格式）",
        responses={
            (200, 'text/markdown'): bytes,
        },
        tags=["screening"],
    )
    def handle_get(self, request, report_id):
        """下载筛选报告。"""
        # 首先尝试从 ResumeData 获取数据（优先，因为包含完整信息）
        resume_data = ResumeData.objects.filter(id=report_id).first()
        
        if resume_data:
            # 从数据库动态生成 Markdown 报告
            md_content = self._generate_markdown_report(resume_data)
            filename = f"{resume_data.candidate_name}简历初筛结果.md"
            
            response = self._create_markdown_response(md_content, filename)
            return response
        
        # 备选：尝试从 ScreeningReport 获取
        report = ScreeningReport.objects.filter(id=report_id).first()
        
        if report:
            # 如果有实际文件，返回文件
            if report.md_file:
                try:
                    response = FileResponse(
                        report.md_file.open('rb'),
                        content_type='text/markdown'
                    )
                    response['Content-Disposition'] = f'attachment; filename="{report.original_filename}"'
                    return response
                except FileNotFoundError:
                    logger.warning(f"Report file not found for report_id={report_id}")
            
            # 如果文件不存在但有关联的 ResumeData
            resume_data = report.resume_data.first()
            if resume_data:
                md_content = self._generate_markdown_report(resume_data)
                filename = report.original_filename or f"{resume_data.candidate_name}简历初筛结果.md"
                response = self._create_markdown_response(md_content, filename)
                return response
        
        # 都找不到，返回404
        return ApiResponse.not_found(message="报告不存在")
    
    def _generate_markdown_report(self, resume_data: ResumeData) -> str:
        """从 ResumeData 生成 Markdown 报告内容。"""
        lines = []
        
        # 标题
        lines.append(f"# {resume_data.candidate_name} 简历初筛报告")
        lines.append("")
        lines.append(f"**岗位**: {resume_data.position_title}")
        lines.append(f"**生成时间**: {resume_data.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 评分部分
        if resume_data.screening_score:
            scores = resume_data.screening_score
            lines.append("## 📊 评分结果")
            lines.append("")
            lines.append("| 评分维度 | 分数 |")
            lines.append("|---------|------|")
            lines.append(f"| 综合评分 | **{scores.get('comprehensive_score', 'N/A')}** |")
            lines.append(f"| HR评分 | {scores.get('hr_score', 'N/A')} |")
            lines.append(f"| 技术评分 | {scores.get('technical_score', 'N/A')} |")
            lines.append(f"| 管理评分 | {scores.get('manager_score', 'N/A')} |")
            lines.append("")
        
        # 筛选总结
        if resume_data.screening_summary:
            lines.append("## 📝 筛选总结")
            lines.append("")
            lines.append(resume_data.screening_summary)
            lines.append("")
        
        # JSON 报告内容（如果有详细分析）
        if resume_data.json_report_content:
            try:
                import json
                json_data = json.loads(resume_data.json_report_content)
                
                # HR分析
                if 'hr_analysis' in json_data:
                    lines.append("## 👔 HR分析")
                    lines.append("")
                    hr = json_data['hr_analysis']
                    if isinstance(hr, dict):
                        for key, value in hr.items():
                            lines.append(f"**{key}**: {value}")
                    else:
                        lines.append(str(hr))
                    lines.append("")
                
                # 技术分析
                if 'technical_analysis' in json_data:
                    lines.append("## 💻 技术分析")
                    lines.append("")
                    tech = json_data['technical_analysis']
                    if isinstance(tech, dict):
                        for key, value in tech.items():
                            lines.append(f"**{key}**: {value}")
                    else:
                        lines.append(str(tech))
                    lines.append("")
                
                # 管理分析
                if 'manager_analysis' in json_data:
                    lines.append("## 📋 管理分析")
                    lines.append("")
                    mgr = json_data['manager_analysis']
                    if isinstance(mgr, dict):
                        for key, value in mgr.items():
                            lines.append(f"**{key}**: {value}")
                    else:
                        lines.append(str(mgr))
                    lines.append("")
                    
            except (json.JSONDecodeError, TypeError):
                # JSON解析失败，直接输出原始内容
                lines.append("## 📄 详细分析")
                lines.append("")
                lines.append(resume_data.json_report_content)
                lines.append("")
        
        # 简历原文
        if resume_data.resume_content:
            lines.append("## 📄 简历原文")
            lines.append("")
            lines.append("```")
            lines.append(resume_data.resume_content)
            lines.append("```")
            lines.append("")
        
        # 页脚
        lines.append("---")
        lines.append("*此报告由 HRM 智能招聘系统自动生成*")
        
        return "\n".join(lines)
    
    def _create_markdown_response(self, content: str, filename: str):
        """创建 Markdown 文件下载响应。"""
        from django.http import HttpResponse
        from urllib.parse import quote
        
        response = HttpResponse(
            content.encode('utf-8'),
            content_type='text/markdown; charset=utf-8'
        )
        # 处理中文文件名
        encoded_filename = quote(filename)
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"
        
        return response
