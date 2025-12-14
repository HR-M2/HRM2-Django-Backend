"""
视频分析数据模型模块。

数据库简化重构：
- 关联到 Resume（原 ResumeData）
- 合并评分字段到 analysis_result JSON
- 删除 candidate_name, position_applied（从关联获取）
"""
from django.db import models
from django.utils import timezone
import uuid


class VideoAnalysis(models.Model):
    """
    视频分析模型 - 简化版
    
    删除的字段:
    - candidate_name: 从 resume 关联获取
    - position_applied: 从 resume.position 获取
    - 多个独立评分字段: 合并到 analysis_result JSON
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', '等待分析'
        PROCESSING = 'processing', '分析中'
        COMPLETED = 'completed', '已完成'
        FAILED = 'failed', '失败'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    
    # 关联简历
    resume = models.ForeignKey(
        'resume.Resume',
        on_delete=models.CASCADE,
        related_name='video_analyses',
        verbose_name="简历"
    )
    
    # 视频信息
    video_file = models.FileField(
        upload_to='videos/%Y/%m/%d/',
        verbose_name="视频文件"
    )
    video_name = models.CharField(max_length=255, verbose_name="视频名称")
    
    # 状态
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="状态"
    )
    error_message = models.TextField(null=True, blank=True, verbose_name="错误信息")
    
    # 分析结果（JSON合并）
    analysis_result = models.JSONField(null=True, blank=True, verbose_name="分析结果")
    # 格式示例:
    # {
    #     "personality": {
    #         "neuroticism": 0.3,
    #         "extraversion": 0.7,
    #         "openness": 0.6,
    #         "agreeableness": 0.8,
    #         "conscientiousness": 0.75
    #     },
    #     "fraud_score": 0.1,
    #     "confidence_score": 0.85,
    #     "summary": "..."
    # }
    
    class Meta:
        db_table = 'video_analyses'
        ordering = ['-created_at']
        verbose_name = "视频分析"
        verbose_name_plural = "视频分析"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.resume.candidate_name} - {self.video_name}"
    
    @property
    def candidate_name(self):
        """从关联简历获取候选人姓名（兼容旧API）。"""
        return self.resume.candidate_name if self.resume else None
    
    @property
    def position_applied(self):
        """从关联简历获取应聘岗位（兼容旧API）。"""
        if self.resume and self.resume.position:
            return self.resume.position.title
        return None
    
    def set_analysis_result(self, result: dict):
        """设置分析结果并更新状态。"""
        self.analysis_result = result
        self.status = self.Status.COMPLETED
        self.save(update_fields=['analysis_result', 'status'])
    
    def mark_failed(self, error_msg: str):
        """标记分析失败。"""
        self.status = self.Status.FAILED
        self.error_message = error_msg
        self.save(update_fields=['status', 'error_message'])
