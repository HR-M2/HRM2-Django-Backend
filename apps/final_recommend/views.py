"""
最终推荐API视图模块 - 与原版 RecruitmentSystemAPI 返回格式保持一致。
"""
import os
import logging
from urllib.parse import unquote
from django.conf import settings
from django.http import FileResponse, JsonResponse

from apps.common.mixins import SafeAPIView
from apps.common.exceptions import ValidationException, NotFoundException

from .models import InterviewEvaluationTask
from .services import EvaluationService

logger = logging.getLogger(__name__)


class InterviewEvaluationView(SafeAPIView):
    """
    面试后评估API
    POST: 启动评估任务
    GET: 获取任务状态
    DELETE: 删除任务
    """
    
    def handle_post(self, request):
        """启动评估任务。"""
        group_id = self.get_param(request, 'group_id', required=True)
        
        # 创建任务
        task = InterviewEvaluationTask.objects.create(
            group_id=group_id,
            status='pending'
        )
        
        # 启动异步任务
        self._start_evaluation(task, group_id)
        
        # 返回与原版一致的格式
        return JsonResponse({
            'status': 'success',
            'message': '面试后评估任务已启动',
            'data': {
                'task_id': str(task.id),
                'status': task.status
            }
        })
    
    def handle_get(self, request, task_id=None):
        """获取任务状态。"""
        if task_id:
            return self._get_task_status(task_id)
        
        group_id = request.GET.get('group_id')
        if group_id:
            return self._get_latest_task_by_group(group_id)
        
        raise ValidationException("缺少任务ID或简历组ID参数")
    
    def handle_delete(self, request, task_id=None):
        """删除任务。"""
        if not task_id:
            raise ValidationException("缺少任务ID参数")
        
        task = self.get_object_or_404(InterviewEvaluationTask, id=task_id)
        
        # 如果文件存在则删除
        if task.result_file:
            try:
                if os.path.isfile(task.result_file.path):
                    os.remove(task.result_file.path)
            except Exception as e:
                logger.error(f"Failed to delete file: {e}")
        
        task.delete()
        
        # 返回与原版一致的格式
        return JsonResponse({
            'status': 'success',
            'message': f'任务 {task_id} 已成功删除'
        })
    
    def _start_evaluation(self, task, group_id):
        """在后台启动评估（使用线程）。"""
        import threading
        
        def run_sync():
            self._process_evaluation(task, group_id)
        
        thread = threading.Thread(target=run_sync)
        thread.daemon = True
        thread.start()
        logger.info(f"Started thread for evaluation {task.id}")
    
    def _process_evaluation(self, task, group_id):
        """同步处理评估。"""
        from datetime import datetime
        from django.core.files.base import ContentFile
        
        def update_progress(speaker_name: str, message_count: int):
            try:
                task.current_speaker = speaker_name
                task.progress = message_count
                task.save()
            except Exception as e:
                logger.error(f"Failed to update progress: {e}")
        
        try:
            task.status = 'processing'
            task.current_speaker = '系统初始化'
            task.progress = 0
            task.save()
            
            messages, speakers = EvaluationService.run_evaluation(
                group_id=group_id,
                progress_callback=update_progress
            )
            
            if not messages:
                raise Exception("评估流程未能生成有效结果")
            
            last_message = messages[-1]
            role = last_message.get('name', '未知角色')
            content = last_message.get('content', '')
            
            filename = f"面试后综合评估报告_{group_id}_{task.id}.md"
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
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}", exc_info=True)
            task.status = 'failed'
            task.error_message = str(e)
            task.current_speaker = '错误'
            task.save()
    
    def _get_task_status(self, task_id):
        """根据ID获取任务状态。"""
        task = self.get_object_or_404(InterviewEvaluationTask, id=task_id)
        
        data = {
            'task_id': str(task.id),
            'group_id': task.group_id,
            'status': task.status,
            'progress': task.progress,
            'current_speaker': task.current_speaker,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        }
        
        if task.status == 'completed' and task.result_file:
            data['result_file'] = task.result_file.url
            data['result_summary'] = task.result_summary
        elif task.status == 'failed':
            data['error_message'] = task.error_message
        
        # 返回与原版一致的格式
        return JsonResponse({
            'status': 'success',
            'data': data
        })
    
    def _get_latest_task_by_group(self, group_id):
        """获取简历组的最新任务。"""
        task = InterviewEvaluationTask.objects.filter(
            group_id=group_id
        ).order_by('-created_at').first()
        
        if not task:
            # 返回与原版一致的格式
            return JsonResponse({
                'status': 'success',
                'data': None
            })
        
        data = {
            'task_id': str(task.id),
            'group_id': task.group_id,
            'status': task.status,
            'progress': task.progress,
            'current_speaker': task.current_speaker,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        }
        
        if task.status == 'completed' and task.result_file:
            data['result_file'] = task.result_file.url
            data['result_summary'] = task.result_summary
        elif task.status == 'failed':
            data['error_message'] = task.error_message
        
        # 返回与原版一致的格式
        return JsonResponse({
            'status': 'success',
            'data': data
        })


class ReportDownloadView(SafeAPIView):
    """
    报告下载API
    GET: 下载评估报告
    """
    
    def handle_get(self, request, file_path):
        """下载报告文件。"""
        decoded_path = unquote(file_path)
        full_path = os.path.join(settings.BASE_DIR, decoded_path.lstrip('/'))
        
        if not os.path.exists(full_path):
            raise NotFoundException("文件不存在")
        
        filename = os.path.basename(full_path)
        
        return FileResponse(
            open(full_path, 'rb'),
            as_attachment=True,
            filename=filename
        )
