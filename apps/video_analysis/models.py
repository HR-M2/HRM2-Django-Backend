"""
视频分析数据模型模块。
"""
from django.db import models
from django.utils import timezone
import uuid


class VideoAnalysis(models.Model):
    """视频分析模型"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', '等待分析'
        PROCESSING = 'processing', '分析中'
        COMPLETED = 'completed', '已完成'
        FAILED = 'failed', '失败'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    
    # 视频信息
    video_name = models.CharField(max_length=255, verbose_name="视频名称")
    video_file = models.FileField(upload_to='video_analysis/videos/%Y/%m/%d/', verbose_name="视频文件")
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name="文件大小")
    
    # 候选人信息
    candidate_name = models.CharField(max_length=100, verbose_name="候选人姓名")
    position_applied = models.CharField(max_length=255, verbose_name="应聘岗位")
    
    # 状态
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING,
        verbose_name="状态"
    )
    error_message = models.TextField(blank=True, null=True, verbose_name="错误信息")
    
    # 分析结果 - 大五人格特质
    fraud_score = models.FloatField(null=True, blank=True, verbose_name="欺诈评分")
    neuroticism_score = models.FloatField(null=True, blank=True, verbose_name="神经质评分")
    extraversion_score = models.FloatField(null=True, blank=True, verbose_name="外倾性评分")
    openness_score = models.FloatField(null=True, blank=True, verbose_name="开放性评分")
    agreeableness_score = models.FloatField(null=True, blank=True, verbose_name="宜人性评分")
    conscientiousness_score = models.FloatField(null=True, blank=True, verbose_name="尽责性评分")
    
    # 摘要
    confidence_score = models.FloatField(null=True, blank=True, verbose_name="置信度评分")
    summary = models.TextField(blank=True, null=True, verbose_name="分析摘要")
    
    class Meta:
        db_table = 'video_analysis'
        ordering = ['-created_at']
        verbose_name = "视频分析"
        verbose_name_plural = "视频分析"
        indexes = [
            models.Index(fields=['candidate_name']),
            models.Index(fields=['position_applied']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    @property
    def analysis_result(self):
        """将评分结果组合成字典格式返回"""
        return {
            "fraud_score": self.fraud_score,
            "neuroticism_score": self.neuroticism_score,
            "extraversion_score": self.extraversion_score,
            "openness_score": self.openness_score,
            "agreeableness_score": self.agreeableness_score,
            "conscientiousness_score": self.conscientiousness_score
        }
    
    def __str__(self):
        return f"{self.candidate_name} - {self.video_name}"
