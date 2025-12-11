"""
简历库数据模型模块。

存储上传但尚未筛选的原始简历。
"""
from django.db import models
from django.utils import timezone
import uuid


class ResumeLibrary(models.Model):
    """简历库模型 - 存储上传但尚未筛选的原始简历"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="上传时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 简历基本信息
    filename = models.CharField(max_length=255, verbose_name="文件名")
    file_hash = models.CharField(max_length=64, unique=True, verbose_name="文件哈希值")
    file_size = models.IntegerField(default=0, verbose_name="文件大小(字节)")
    file_type = models.CharField(max_length=50, default='', verbose_name="文件类型")
    
    # 简历内容
    content = models.TextField(verbose_name="简历内容(文本)")
    
    # 候选人信息（可选，可后续提取）
    candidate_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="候选人姓名")
    
    # 状态标记
    is_screened = models.BooleanField(default=False, verbose_name="是否已筛选")
    is_assigned = models.BooleanField(default=False, verbose_name="是否已分配岗位")
    
    # 备注
    notes = models.TextField(blank=True, null=True, verbose_name="备注")
    
    class Meta:
        db_table = 'resume_library'
        ordering = ['-created_at']
        verbose_name = "简历库"
        verbose_name_plural = "简历库"
        indexes = [
            models.Index(fields=['filename']),
            models.Index(fields=['file_hash']),
            models.Index(fields=['candidate_name']),
            models.Index(fields=['is_screened']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.filename} - {self.candidate_name or '未知'}"
