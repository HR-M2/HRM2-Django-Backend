"""
简历管理数据模型模块。

数据库简化重构：
- 合并 ResumeLibrary + ResumeData -> Resume
- 删除 ResumeGroup（用 Position 替代）
- 删除 ScreeningReport（报告内容存入 Resume）
"""
from django.db import models
from django.utils import timezone
import uuid


class Resume(models.Model):
    """
    简历模型 - 核心表
    
    合并原 ResumeLibrary 和 ResumeData
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', '待筛选'
        SCREENED = 'screened', '已筛选'
        INTERVIEWING = 'interviewing', '面试中'
        ANALYZED = 'analyzed', '已分析'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # === 文件信息（原 ResumeLibrary）===
    filename = models.CharField(max_length=255, verbose_name="文件名")
    file_hash = models.CharField(max_length=64, unique=True, verbose_name="文件哈希")
    file_size = models.IntegerField(default=0, verbose_name="文件大小")
    file_type = models.CharField(max_length=50, blank=True, verbose_name="文件类型")
    
    # === 候选人信息 ===
    candidate_name = models.CharField(max_length=100, verbose_name="候选人姓名")
    content = models.TextField(verbose_name="简历内容")
    
    # === 岗位关联（简化，直接外键）===
    position = models.ForeignKey(
        'position_settings.Position',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resumes',
        verbose_name="应聘岗位"
    )
    
    # === 状态管理 ===
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="状态"
    )
    
    # === 筛选结果（内嵌，原 ResumeData 部分字段）===
    screening_result = models.JSONField(null=True, blank=True, verbose_name="筛选结果")
    # 格式示例:
    # {
    #     "score": 85,
    #     "dimensions": {...},
    #     "summary": "..."
    # }
    
    screening_report = models.TextField(null=True, blank=True, verbose_name="筛选报告MD")
    
    # === 备注 ===
    notes = models.TextField(blank=True, verbose_name="备注")
    
    class Meta:
        db_table = 'resumes'
        ordering = ['-created_at']
        verbose_name = "简历"
        verbose_name_plural = "简历"
        indexes = [
            models.Index(fields=['file_hash']),
            models.Index(fields=['candidate_name']),
            models.Index(fields=['status']),
            models.Index(fields=['position']),
        ]
    
    def __str__(self):
        return f"{self.filename} - {self.candidate_name}"
    
    def to_dict(self):
        """转换为字典格式（兼容旧API）。"""
        return {
            "id": str(self.id),
            "filename": self.filename,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "candidate_name": self.candidate_name,
            "content": self.content,
            "position_id": str(self.position_id) if self.position_id else None,
            "position_title": self.position.title if self.position else None,
            "status": self.status,
            "screening_result": self.screening_result,
            "screening_report": self.screening_report,
            "notes": self.notes,
            "is_screened": self.status != self.Status.PENDING,
            "is_assigned": self.position_id is not None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def update_status(self, new_status: str):
        """更新简历状态。"""
        if new_status in [choice[0] for choice in self.Status.choices]:
            self.status = new_status
            self.save(update_fields=['status', 'updated_at'])
    
    def set_screening_result(self, result: dict, report_md: str = None):
        """设置筛选结果并更新状态。"""
        self.screening_result = result
        if report_md:
            self.screening_report = report_md
        self.status = self.Status.SCREENED
        self.save(update_fields=['screening_result', 'screening_report', 'status', 'updated_at'])
    
    def assign_to_position(self, position):
        """分配到岗位。"""
        self.position = position
        self.save(update_fields=['position', 'updated_at'])
    
    def unassign_position(self):
        """取消岗位分配。"""
        self.position = None
        self.save(update_fields=['position', 'updated_at'])
