"""
最终推荐数据模型模块。
"""
from django.db import models
from django.utils import timezone
import uuid


class InterviewEvaluationTask(models.Model):
    """面试后评估任务模型"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', '等待处理'
        PROCESSING = 'processing', '处理中'
        COMPLETED = 'completed', '已完成'
        FAILED = 'failed', '失败'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 任务信息
    group_id = models.CharField(max_length=255, verbose_name="简历组ID")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="状态"
    )
    progress = models.IntegerField(default=0, verbose_name="进度(对话轮数)")
    current_speaker = models.CharField(max_length=100, blank=True, null=True, verbose_name="当前发言者")
    
    # 结果
    result_file = models.FileField(
        upload_to='interview_evaluation_reports/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name="结果文件"
    )
    result_summary = models.TextField(blank=True, null=True, verbose_name="结果摘要")
    error_message = models.TextField(blank=True, null=True, verbose_name="错误信息")
    
    class Meta:
        db_table = 'interview_evaluation_tasks'
        ordering = ['-created_at']
        verbose_name = "面试评估任务"
        verbose_name_plural = "面试评估任务"
    
    def __str__(self):
        return f"面试评估任务 {self.group_id} ({self.status})"
