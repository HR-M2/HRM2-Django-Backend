"""
岗位设置数据模型模块。

数据库简化重构：
- PositionCriteria -> Position (重命名+简化)
- ResumePositionAssignment -> 删除 (改为 Resume.position 外键)
"""
from django.db import models
from django.utils import timezone
import uuid


class Position(models.Model):
    """
    岗位模型 - 简化版
    
    合并原 PositionCriteria 的多个字段为 requirements JSON
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 基本信息
    title = models.CharField(max_length=255, verbose_name="岗位名称")
    department = models.CharField(max_length=255, blank=True, verbose_name="部门")
    description = models.TextField(blank=True, verbose_name="岗位描述")
    
    # 岗位要求（JSON合并）
    requirements = models.JSONField(default=dict, verbose_name="岗位要求")
    # 格式示例:
    # {
    #     "required_skills": ["Python", "Django"],
    #     "optional_skills": ["React", "Docker"],
    #     "min_experience": 3,
    #     "education": ["本科", "硕士"],
    #     "certifications": [],
    #     "salary_range": [15000, 25000],
    #     "project_requirements": {}
    # }
    
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    
    class Meta:
        db_table = 'positions'
        ordering = ['-created_at']
        verbose_name = "岗位"
        verbose_name_plural = "岗位"
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    def to_dict(self):
        """转换为字典格式（兼容旧API）。"""
        reqs = self.requirements or {}
        salary_range = reqs.get('salary_range', [0, 0])
        return {
            "id": str(self.id),
            "position": self.title,  # 兼容旧字段名
            "title": self.title,
            "department": self.department,
            "description": self.description,
            "required_skills": reqs.get('required_skills', []),
            "optional_skills": reqs.get('optional_skills', []),
            "min_experience": reqs.get('min_experience', 0),
            "education": reqs.get('education', []),
            "certifications": reqs.get('certifications', []),
            "salary_range": salary_range,
            "salary_min": salary_range[0] if len(salary_range) > 0 else 0,
            "salary_max": salary_range[1] if len(salary_range) > 1 else 0,
            "project_requirements": reqs.get('project_requirements', {}),
            "is_active": self.is_active,
            "resume_count": self.get_resume_count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_resume_count(self):
        """动态计算简历数量（不再使用缓存字段）。"""
        return self.resumes.count()
    
    @classmethod
    def from_legacy_data(cls, data: dict) -> 'Position':
        """从旧格式数据创建岗位（用于API兼容）。"""
        requirements = {
            'required_skills': data.get('required_skills', []),
            'optional_skills': data.get('optional_skills', []),
            'min_experience': data.get('min_experience', 0),
            'education': data.get('education', []),
            'certifications': data.get('certifications', []),
            'salary_range': [
                data.get('salary_min', 0),
                data.get('salary_max', 0)
            ],
            'project_requirements': data.get('project_requirements', {}),
        }
        return cls(
            title=data.get('position', data.get('title', '')),
            department=data.get('department', ''),
            description=data.get('description', ''),
            requirements=requirements,
            is_active=data.get('is_active', True),
        )


# 保留旧模型别名以便于渐进式迁移（将在 Phase 8 删除）
PositionCriteria = Position
