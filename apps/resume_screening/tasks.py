"""
简历筛选的Celery任务模块。
"""
import logging
from celery import shared_task
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def run_screening_task(self, task_id: str, position_data: dict, resumes_data: list):
    """
    在后台运行简历筛选的Celery任务。
    
    参数:
        task_id: ResumeScreeningTask的UUID
        position_data: 岗位/职位信息
        resumes_data: 简历数据字典列表
    """
    from .models import ResumeScreeningTask
    from .services import ScreeningService, ReportService
    from apps.common.utils import extract_name_from_filename
    
    try:
        task = ResumeScreeningTask.objects.get(id=task_id)
        task.status = 'running'
        task.save()
        
        logger.info(f"Starting screening task {task_id} with {len(resumes_data)} resumes")
        
        # 运行筛选
        results = ScreeningService.run_screening(
            task=task,
            position_data=position_data,
            resumes_data=resumes_data,
            run_chat=True
        )
        
        # 保存结果，跟踪重复简历
        new_count = 0
        duplicate_count = 0
        
        for resume in resumes_data:
            candidate_name = extract_name_from_filename(resume['name'])
            result = results.get(candidate_name, {})
            
            if result:
                # 保存到ResumeData
                resume_data, is_new = ReportService.save_resume_data(
                    task=task,
                    position_data=position_data,
                    candidate_name=candidate_name,
                    resume_content=resume['content'],
                    screening_result=result
                )
                
                if is_new:
                    new_count += 1
                    # 只为新简历保存报告
                    ReportService.save_report_to_model(
                        task=task,
                        candidate_name=candidate_name,
                        md_content=result.get('md_content', ''),
                        json_content=result.get('json_content', '{}'),
                        resume_content=resume['content']
                    )
                else:
                    duplicate_count += 1
        
        # 记录统计信息
        if duplicate_count > 0:
            logger.info(f"筛选完成: {new_count} 份新简历, {duplicate_count} 份重复简历已跳过")
        
        # 标记任务为已完成
        task.status = 'completed'
        task.progress = 100
        task.current_step = task.total_steps
        task.current_speaker = None
        task.save()
        
        logger.info(f"Screening task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Screening task {task_id} failed: {e}", exc_info=True)
        
        try:
            task = ResumeScreeningTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error_message = str(e)
            task.current_speaker = None
            task.save()
        except Exception:
            pass
        
        # 失败时重试
        raise self.retry(exc=e, countdown=60)


@shared_task
def cleanup_old_tasks(days: int = 30):
    """
    清理旧的已完成/失败任务。
    
    参数:
        days: 保留任务的天数
    """
    from datetime import timedelta
    from django.utils import timezone
    from .models import ResumeScreeningTask
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    old_tasks = ResumeScreeningTask.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['completed', 'failed']
    )
    
    count = old_tasks.count()
    old_tasks.delete()
    
    logger.info(f"Cleaned up {count} old screening tasks")
    return count
