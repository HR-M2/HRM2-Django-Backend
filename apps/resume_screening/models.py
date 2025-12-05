"""
简历筛选数据模型模块。
"""
from django.db import models
from django.utils import timezone
import uuid


class ResumeScreeningTask(models.Model):
    """简历初筛任务模型"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', '等待中'
        RUNNING = 'running', '进行中'
        COMPLETED = 'completed', '已完成'
        FAILED = 'failed', '失败'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING,
        verbose_name="状态"
    )
    progress = models.IntegerField(default=0, verbose_name="进度百分比")
    current_step = models.IntegerField(default=0, verbose_name="当前步骤")
    total_steps = models.IntegerField(default=1, verbose_name="总步骤数")
    error_message = models.TextField(blank=True, null=True, verbose_name="错误信息")
    current_speaker = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="当前发言者"
    )
    position_data = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name="岗位信息"
    )

    class Meta:
        db_table = 'resume_screening_tasks'
        ordering = ['-created_at']
        verbose_name = "简历筛选任务"
        verbose_name_plural = "简历筛选任务"


class ScreeningReport(models.Model):
    """初筛报告模型"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        ResumeScreeningTask, 
        on_delete=models.CASCADE, 
        related_name='reports',
        verbose_name="关联任务"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    md_file = models.FileField(
        upload_to='screening_reports/%Y/%m/%d/', 
        verbose_name="MD报告文件"
    )
    original_filename = models.CharField(max_length=255, verbose_name="原始文件名")
    resume_content = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="简历内容"
    )
    json_report_content = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="JSON报告内容"
    )

    class Meta:
        db_table = 'screening_reports'
        ordering = ['-created_at']
        verbose_name = "筛选报告"
        verbose_name_plural = "筛选报告"


class ResumeGroup(models.Model):
    """简历组模型 - 用于组织具有相同岗位信息的简历"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', '待分析'
        INTERVIEW_ANALYSIS = 'interview_analysis', '面试分析中'
        INTERVIEW_COMPLETED = 'interview_analysis_completed', '面试分析已完成'
        COMPREHENSIVE = 'comprehensive_screening', '综合筛选中'
        COMPLETED = 'completed', '已完成'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    
    # 岗位信息
    position_title = models.CharField(max_length=255, verbose_name="岗位名称")
    position_details = models.JSONField(verbose_name="岗位详细信息")
    position_hash = models.CharField(
        max_length=64, 
        unique=True, 
        verbose_name="岗位信息哈希值"
    )
    
    # 简历组信息
    group_name = models.CharField(max_length=255, verbose_name="简历组名称")
    description = models.TextField(blank=True, null=True, verbose_name="组描述")
    resume_count = models.IntegerField(default=0, verbose_name="简历数量")
    
    # 状态
    status = models.CharField(
        max_length=30, 
        choices=Status.choices, 
        default=Status.PENDING, 
        verbose_name="状态"
    )
    
    class Meta:
        db_table = 'resume_groups'
        ordering = ['-created_at']
        verbose_name = "简历组"
        verbose_name_plural = "简历组"
        indexes = [
            models.Index(fields=['position_title']),
            models.Index(fields=['position_hash']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]


class ResumeData(models.Model):
    """简历数据统一管理模型"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    
    # 岗位信息
    position_title = models.CharField(max_length=255, verbose_name="岗位名称")
    position_details = models.JSONField(verbose_name="岗位详细信息")
    
    # 候选人信息
    candidate_name = models.CharField(max_length=100, verbose_name="候选人姓名")
    resume_content = models.TextField(verbose_name="简历内容")
    
    # 筛选结果
    screening_score = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name="筛选评分"
    )
    screening_summary = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="筛选总结"
    )
    
    # 文件存储
    resume_file_hash = models.CharField(
        max_length=64, 
        unique=True, 
        verbose_name="简历文件哈希值"
    )
    report_md_file = models.FileField(
        upload_to='screening_reports/%Y/%m/%d/', 
        null=True, 
        blank=True, 
        verbose_name="报告MD文件"
    )
    report_json_file = models.FileField(
        upload_to='screening_reports/%Y/%m/%d/', 
        null=True, 
        blank=True, 
        verbose_name="报告JSON文件"
    )
    json_report_content = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="JSON报告内容"
    )
    
    # 关联关系
    task = models.ForeignKey(
        ResumeScreeningTask, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resume_data',
        verbose_name="关联任务"
    )
    report = models.ForeignKey(
        ScreeningReport, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resume_data',
        verbose_name="关联报告"
    )
    group = models.ForeignKey(
        ResumeGroup, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resumes',
        verbose_name="关联简历组"
    )
    video_analysis = models.OneToOneField(
        'video_analysis.VideoAnalysis', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='linked_resume_data',
        verbose_name="关联视频分析"
    )
    
    class Meta:
        db_table = 'resume_data'
        ordering = ['-created_at']
        verbose_name = "简历数据"
        verbose_name_plural = "简历数据"
        indexes = [
            models.Index(fields=['candidate_name']),
            models.Index(fields=['position_title']),
            models.Index(fields=['resume_file_hash']),
            models.Index(fields=['created_at']),
        ]
