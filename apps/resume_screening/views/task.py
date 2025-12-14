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
        """获取任务关联的简历数据（通过 ManyToMany）。"""
        # 通过 task.resumes 获取该任务实际筛选的简历
        resumes = task.resumes.all()
        result = []
        
        for resume in resumes:
            # 构建符合前端 ScreeningScore 接口的分数对象
            screening_score = None
            if resume.screening_result:
                screening_score = {
                    "comprehensive_score": resume.screening_result.get('comprehensive_score') or resume.screening_result.get('score'),
                    "hr_score": resume.screening_result.get('hr_score'),
                    "technical_score": resume.screening_result.get('technical_score'),
                    "manager_score": resume.screening_result.get('manager_score'),
                }
            
            data = {
                "id": str(resume.id),
                "candidate_name": resume.candidate_name,
                "position_title": task.position.title if task.position else None,
                "screening_score": screening_score,
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
        """下载筛选报告。
        
        数据库简化重构后，报告内容存储在 Resume.screening_report 字段中。
        report_id 现在是 resume_id。
        """
        # 从 Resume 获取数据
        resume = Resume.objects.filter(id=report_id).first()
        
        if resume:
            # 如果有已存储的报告，直接返回
            if resume.screening_report:
                md_content = resume.screening_report
            else:
                # 从数据库动态生成 Markdown 报告
                md_content = self._generate_markdown_report(resume)
            
            filename = f"{resume.candidate_name}简历初筛结果.md"
            response = self._create_markdown_response(md_content, filename)
            return response
        
        # 找不到，返回404
        return ApiResponse.not_found(message="报告不存在")
    
    def _generate_markdown_report(self, resume: Resume) -> str:
        """从 Resume 生成 Markdown 报告内容。
        
        数据库简化重构：
        - resume.screening_result JSON 包含 score, dimensions, summary
        - resume.position 外键获取岗位信息
        """
        lines = []
        
        # 标题
        lines.append(f"# {resume.candidate_name} 简历初筛报告")
        lines.append("")
        position_title = resume.position.title if resume.position else "未指定"
        lines.append(f"**岗位**: {position_title}")
        lines.append(f"**生成时间**: {resume.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 评分部分
        if resume.screening_result:
            result = resume.screening_result
            lines.append("## 📊 评分结果")
            lines.append("")
            
            # 综合评分
            if 'score' in result:
                lines.append(f"**综合评分**: {result.get('score', 'N/A')}")
                lines.append("")
            
            # 维度评分
            if 'dimensions' in result and isinstance(result['dimensions'], dict):
                lines.append("| 评分维度 | 分数 |")
                lines.append("|---------|------|")
                for dim_name, dim_score in result['dimensions'].items():
                    lines.append(f"| {dim_name} | {dim_score} |")
                lines.append("")
        
        # 筛选总结
        if resume.screening_result and resume.screening_result.get('summary'):
            lines.append("## 📝 筛选总结")
            lines.append("")
            lines.append(resume.screening_result['summary'])
            lines.append("")
        
        # 简历原文
        if resume.content:
            lines.append("## 📄 简历原文")
            lines.append("")
            lines.append("```")
            lines.append(resume.content)
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
