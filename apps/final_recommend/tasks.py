"""
最终推荐的Celery任务模块。
"""
import logging
from celery import shared_task
from datetime import datetime
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def run_evaluation_task(self, task_id: str, group_id: str):
    """
    运行面试后评估的Celery任务。
    
    参数:
        task_id: InterviewEvaluationTask的UUID
        group_id: ResumeGroup的UUID
    """
    from .models import InterviewEvaluationTask
    from .services import EvaluationService
    
    def update_progress(speaker_name: str, message_count: int):
        """进度回调函数。"""
        try:
            task = InterviewEvaluationTask.objects.get(id=task_id)
            task.current_speaker = speaker_name
            task.progress = message_count
            task.save()
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")
    
    try:
        task = InterviewEvaluationTask.objects.get(id=task_id)
        task.status = 'processing'
        task.current_speaker = '系统初始化'
        task.progress = 0
        task.save()
        
        logger.info(f"Starting evaluation task {task_id} for group {group_id}")
        
        # 运行评估
        messages, speakers = EvaluationService.run_evaluation(
            group_id=group_id,
            progress_callback=update_progress
        )
        
        if not messages:
            raise Exception("评估流程未能生成有效结果")
        
        # 保存结果
        last_message = messages[-1]
        role = last_message.get('name', '未知角色')
        content = last_message.get('content', '')
        
        # 生成报告
        filename = f"面试后综合评估报告_{group_id}_{task_id}.md"
        report_content = f"""# 企业招聘面试后综合评估报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**简历组ID**: {group_id}

**最终发言 - {role}**

{content}
"""
        
        task.result_file.save(filename, ContentFile(report_content.encode('utf-8')))
        task.result_summary = content[:500]
        task.status = 'completed'
        task.progress = len(messages)
        task.current_speaker = '完成'
        task.save()
        
        logger.info(f"Evaluation task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Evaluation task {task_id} failed: {e}", exc_info=True)
        
        try:
            task = InterviewEvaluationTask.objects.get(id=task_id)
            task.status = 'failed'
            task.error_message = str(e)
            task.current_speaker = '错误'
            task.save()
        except Exception:
            pass
        
        raise self.retry(exc=e, countdown=60)
