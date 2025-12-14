"""
简历筛选API视图模块 - 与原版 RecruitmentSystemAPI 返回格式保持一致。

数据库简化重构：
- 使用 ScreeningTask 模型（原 ResumeScreeningTask 已重命名+简化）
- 使用 Resume 模型（原 ResumeData 已合并到 Resume）
- ScreeningReport 已删除（报告内容存入 Resume）
"""
import logging
from django.conf import settings

from drf_spectacular.utils import extend_schema

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.exceptions import ValidationException
from apps.common.utils import extract_name_from_filename, generate_hash
from apps.common.schemas import (
    api_response,
    TaskSubmitSerializer, TaskStatusSerializer,
)

from ..models import ScreeningTask
from apps.resume.models import Resume
from apps.position_settings.models import Position
from ..services import ScreeningService
from ..serializers import ResumeScreeningInputSerializer

logger = logging.getLogger(__name__)


class ResumeScreeningView(SafeAPIView):
    """
    简历初筛API
    POST: 提交简历筛选任务
    """
    
    @extend_schema(
        summary="提交简历筛选任务",
        description="提交简历筛选任务，后台异步处理",
        responses={202: api_response(TaskSubmitSerializer(), "ScreeningSubmit")},
        tags=["screening"],
    )
    def handle_post(self, request):
        """提交简历筛选任务。"""
        # 验证输入
        serializer = ResumeScreeningInputSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.validation_error(
                errors=serializer.errors,
                message="参数验证失败"
            )
        
        try:
            # 解析输入数据
            position_data, resumes_data = ScreeningService.parse_input_data(request.data)
            
            # 获取或创建岗位
            position_title = position_data.get('position', '未指定岗位')
            position, _ = Position.objects.get_or_create(
                title=position_title,
                defaults={
                    'requirements': position_data,
                    'is_active': True
                }
            )
            
            # 创建任务（使用新的 ScreeningTask 模型）
            task = ScreeningTask.objects.create(
                position=position,
                status='pending',
                progress=0,
                total_count=len(resumes_data),
                processed_count=0
            )
            
            # 立即保存简历数据到 Resume 模型
            for resume in resumes_data:
                candidate_name = extract_name_from_filename(resume['name'])
                content = resume['content']
                file_hash = generate_hash(content)
                
                # 检查是否已存在
                existing = Resume.objects.filter(file_hash=file_hash).first()
                if not existing:
                    Resume.objects.create(
                        filename=resume['name'],
                        file_hash=file_hash,
                        file_size=len(content.encode('utf-8')),
                        candidate_name=candidate_name,
                        content=content,
                        position=position,
                        status=Resume.Status.PENDING
                    )
            
            # 启动异步任务（使用Celery或线程）
            self._start_screening_task(task, position_data, resumes_data)
            
            # 返回与原版一致的格式
            return ApiResponse.accepted(
                data={
                    "status": "submitted",
                    "task_id": str(task.id)
                },
                message="简历筛选任务已提交，正在后台处理"
            )
            
        except ValidationException as e:
            return ApiResponse.validation_error(
                errors=e.errors,
                message=e.message
            )
    
    def _start_screening_task(self, task, position_data, resumes_data):
        """在后台启动筛选任务（使用线程）。"""
        import threading
        thread = threading.Thread(
            target=self._run_screening_sync,
            args=(task, position_data, resumes_data)
        )
        thread.daemon = True
        thread.start()
        logger.info(f"Started thread for screening task {task.id}")
    
    def _run_screening_sync(self, task, position_data, resumes_data):
        """同步运行筛选（用于线程回退）。"""
        import hashlib
        from apps.common.utils import extract_name_from_filename
        from django.core.cache import cache
        
        try:
            # 检查是否设置了强制错误标志（测试钩子）
            error_config = cache.get('test_force_screening_error')
            if error_config and error_config.get('active', False):
                error_message = error_config.get('message', '测试：强制触发的简历筛选任务失败')
                error_type = error_config.get('type', 'runtime')
                
                logger.info(f"Force error trigger: {error_message} (type: {error_type})")
                
                if error_type == 'validation':
                    from apps.common.exceptions import ValidationException
                    raise ValidationException(error_message)
                elif error_type == 'service':
                    from apps.common.exceptions import ServiceException
                    raise ServiceException(error_message)
                else:  # runtime
                    raise RuntimeError(error_message)
            
            task.status = 'running'
            task.save()
            
            results = ScreeningService.run_screening(
                task=task,
                position_data=position_data,
                resumes_data=resumes_data,
                run_chat=True
            )
            
            # 保存结果到 Resume 模型
            processed_count = 0
            
            for resume in resumes_data:
                candidate_name = extract_name_from_filename(resume['name'])
                content = resume['content']
                file_hash = generate_hash(content)
                result = results.get(candidate_name, {})
                
                # 查找或创建 Resume
                resume_obj, _ = Resume.objects.get_or_create(
                    file_hash=file_hash,
                    defaults={
                        'filename': resume['name'],
                        'file_size': len(content.encode('utf-8')),
                        'candidate_name': candidate_name,
                        'content': content,
                        'position': task.position,
                    }
                )
                
                # 更新筛选结果
                if result:
                    scores = result.get('scores', {})
                    screening_result = {
                        'score': scores.get('comprehensive_score', result.get('comprehensive_score', result.get('score'))),
                        'hr_score': scores.get('hr_score'),
                        'technical_score': scores.get('technical_score'),
                        'manager_score': scores.get('manager_score'),
                        'comprehensive_score': scores.get('comprehensive_score', result.get('comprehensive_score')),
                        'dimensions': result.get('dimensions', {}),
                        'summary': result.get('summary', result.get('screening_summary', '')),
                    }
                    resume_obj.set_screening_result(screening_result, result.get('md_content'))
                
                # 将简历添加到任务的多对多关系中
                task.resumes.add(resume_obj)
                
                processed_count += 1
                task.update_progress(processed_count, len(resumes_data))
            
            task.mark_completed()
            
        except Exception as e:
            logger.error(f"Screening failed: {e}", exc_info=True)
            task.mark_failed(str(e))


class ScreeningTaskStatusView(SafeAPIView):
    """
    查询筛选任务状态API
    GET: 获取任务状态和结果
    """
    
    @extend_schema(
        summary="获取筛选任务状态",
        description="获取指定筛选任务的状态和结果",
        responses={200: api_response(TaskStatusSerializer(), "ScreeningTaskStatus")},
        tags=["screening"],
    )
    def handle_get(self, request, task_id):
        """获取任务状态。"""
        task = self.get_object_or_404(ScreeningTask, id=task_id)
        
        response_data = {
            "task_id": str(task.id),
            "status": task.status,
            "progress": task.progress,
            "current_step": task.processed_count,
            "total_steps": task.total_count,
            "created_at": task.created_at.isoformat()
        }
        
        # 获取关联简历数据
        response_data['resume_data'] = self._get_resume_data(task)
        
        # 如果失败则添加错误信息
        if task.status == 'failed' and task.error_message:
            response_data['error_message'] = task.error_message
        
        # 返回与原版一致的格式
        return ApiResponse.success(data=response_data)
    
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
