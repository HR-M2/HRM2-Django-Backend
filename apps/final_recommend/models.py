"""
最终推荐数据模型模块。
"""
from django.db import models
from django.utils import timezone
import uuid


class CandidateComprehensiveAnalysis(models.Model):
    """
    单人综合分析结果模型。
    
    保存基于 Rubric 量表的多维度评估结果。
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 关联简历
    resume_data = models.ForeignKey(
        'resume_screening.ResumeData',
        on_delete=models.CASCADE,
        related_name='comprehensive_analyses',
        verbose_name="关联简历"
    )
    
    # 评估结果
    final_score = models.FloatField(verbose_name="综合得分")
    recommendation_level = models.CharField(max_length=50, verbose_name="推荐等级")
    recommendation_label = models.CharField(max_length=50, verbose_name="推荐标签")
    recommendation_action = models.TextField(verbose_name="建议行动")
    
    # 各维度评分详情（JSON）
    dimension_scores = models.JSONField(default=dict, verbose_name="维度评分详情")
    
    # 综合报告文本
    comprehensive_report = models.TextField(verbose_name="综合分析报告")
    
    # 输入数据快照（便于追溯）
    input_data_snapshot = models.JSONField(default=dict, verbose_name="输入数据快照")
    
    class Meta:
        db_table = 'candidate_comprehensive_analyses'
        ordering = ['-created_at']
        verbose_name = "候选人综合分析"
        verbose_name_plural = "候选人综合分析"
    
    def __str__(self):
        return f"{self.resume_data.candidate_name} 综合分析 ({self.recommendation_label})"


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
