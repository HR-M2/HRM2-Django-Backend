"""
简历筛选数据模型模块。

数据库简化重构：
- ResumeScreeningTask -> ScreeningTask (重命名+简化)
- ScreeningReport -> 删除 (报告内容存入 Resume)
- ResumeGroup -> 删除 (用 Position 替代)
- ResumeData -> 删除 (合并到 Resume)
"""
from django.db import models
from django.utils import timezone
import uuid


class ScreeningTask(models.Model):
    """
    筛选任务模型 - 简化版
    
    删除的字段:
    - current_step / total_steps: 用 progress 百分比替代
    - current_speaker: Agent相关，移到运行时状态
    - position_data: 通过 position FK 获取
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', '等待中'
        RUNNING = 'running', '进行中'
        COMPLETED = 'completed', '已完成'
        FAILED = 'failed', '失败'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    
    # 关联岗位
    position = models.ForeignKey(
        'position_settings.Position',
        on_delete=models.CASCADE,
        related_name='screening_tasks',
        verbose_name="岗位"
    )
    
    # 关联简历（多对多）- 记录该任务实际筛选的简历
    resumes = models.ManyToManyField(
        'resume.Resume',
        related_name='screening_tasks',
        blank=True,
        verbose_name="筛选的简历"
    )
    
    # 任务状态
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="状态"
    )
    progress = models.IntegerField(default=0, verbose_name="进度%")
    total_count = models.IntegerField(default=0, verbose_name="总数量")
    processed_count = models.IntegerField(default=0, verbose_name="已处理数量")
    error_message = models.TextField(null=True, blank=True, verbose_name="错误信息")
    
    class Meta:
        db_table = 'screening_tasks'
        ordering = ['-created_at']
        verbose_name = "筛选任务"
        verbose_name_plural = "筛选任务"
    
    def __str__(self):
        return f"筛选任务 {self.id} - {self.position.title}"
    
    def update_progress(self, processed: int, total: int = None):
        """更新任务进度。"""
        self.processed_count = processed
        if total is not None:
            self.total_count = total
        if self.total_count > 0:
            self.progress = int((processed / self.total_count) * 100)
        self.save(update_fields=['processed_count', 'total_count', 'progress'])
    
    def mark_completed(self):
        """标记任务完成。"""
        self.status = self.Status.COMPLETED
        self.progress = 100
        self.save(update_fields=['status', 'progress'])
    
    def mark_failed(self, error_msg: str):
        """标记任务失败。"""
        self.status = self.Status.FAILED
        self.error_message = error_msg
        self.save(update_fields=['status', 'error_message'])


