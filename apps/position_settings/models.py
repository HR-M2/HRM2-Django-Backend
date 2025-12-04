"""
岗位设置数据模型模块。
"""
from django.db import models
from django.utils import timezone
import uuid


class PositionCriteria(models.Model):
    """岗位招聘标准模型"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 岗位信息
    position = models.CharField(max_length=255, verbose_name="职位名称")
    department = models.CharField(max_length=255, blank=True, verbose_name="部门")
    
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
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    class Meta:
        db_table = 'position_criteria'
        ordering = ['-created_at']
        verbose_name = "岗位招聘标准"
        verbose_name_plural = "岗位招聘标准"
    
    def to_dict(self):
        """转换为字典格式。"""
        return {
            "position": self.position,
            "required_skills": self.required_skills,
            "optional_skills": self.optional_skills,
            "min_experience": self.min_experience,
            "education": self.education,
            "certifications": self.certifications,
            "salary_range": [self.salary_min, self.salary_max],
            "project_requirements": self.project_requirements
        }
