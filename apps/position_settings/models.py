"""
岗位设置数据模型模块。
"""
from django.db import models
from django.utils import timezone
import uuid


class PositionCriteria(models.Model):
    """岗位招聘标准模型 - 支持多岗位，每个岗位即为一个简历组"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 岗位信息
    position = models.CharField(max_length=255, verbose_name="职位名称")
    department = models.CharField(max_length=255, blank=True, verbose_name="部门")
    description = models.TextField(blank=True, verbose_name="岗位描述")
    
    # 要求
    required_skills = models.JSONField(default=list, verbose_name="必备技能")
    optional_skills = models.JSONField(default=list, verbose_name="加分技能")
    min_experience = models.IntegerField(default=0, verbose_name="最低工作年限")
    education = models.JSONField(default=list, verbose_name="学历要求")
    certifications = models.JSONField(default=list, verbose_name="证书要求")
    
    # 薪资
    salary_min = models.IntegerField(default=0, verbose_name="最低薪资")
    salary_max = models.IntegerField(default=0, verbose_name="最高薪资")
    
    # 项目经验要求
    project_requirements = models.JSONField(default=dict, verbose_name="项目经验要求")
    
    # 状态管理
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    # 简历数量缓存（便于快速查询）
    resume_count = models.IntegerField(default=0, verbose_name="简历数量")
    
    class Meta:
        db_table = 'position_criteria'
        ordering = ['-created_at']
        verbose_name = "岗位招聘标准"
        verbose_name_plural = "岗位招聘标准"
        indexes = [
            models.Index(fields=['position']),
            models.Index(fields=['is_active']),
        ]
    
    def to_dict(self):
        """转换为字典格式。"""
        return {
            "id": str(self.id),
            "position": self.position,
            "department": self.department,
            "description": self.description,
            "required_skills": self.required_skills,
            "optional_skills": self.optional_skills,
            "min_experience": self.min_experience,
            "education": self.education,
            "certifications": self.certifications,
            "salary_range": [self.salary_min, self.salary_max],
            "project_requirements": self.project_requirements,
            "is_active": self.is_active,
            "resume_count": self.resume_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def update_resume_count(self):
        """更新简历数量缓存。"""
        self.resume_count = self.resume_assignments.count()
        self.save(update_fields=['resume_count'])
    
    def get_assigned_resumes(self):
        """获取分配到该岗位的所有简历。"""
        from apps.resume_screening.models import ResumeData
        resume_ids = self.resume_assignments.values_list('resume_data_id', flat=True)
        return ResumeData.objects.filter(id__in=resume_ids)


class ResumePositionAssignment(models.Model):
    """简历-岗位分配中间表，支持多对多关系"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.ForeignKey(
        PositionCriteria,
        on_delete=models.CASCADE,
        related_name='resume_assignments',
        verbose_name="岗位"
    )
    resume_data = models.ForeignKey(
        'resume_screening.ResumeData',
        on_delete=models.CASCADE,
        related_name='position_assignments',
        verbose_name="简历数据"
    )
    assigned_at = models.DateTimeField(default=timezone.now, verbose_name="分配时间")
    notes = models.TextField(blank=True, verbose_name="备注")
    
    class Meta:
        db_table = 'resume_position_assignments'
        unique_together = ['position', 'resume_data']
        ordering = ['-assigned_at']
        verbose_name = "简历岗位分配"
        verbose_name_plural = "简历岗位分配"
