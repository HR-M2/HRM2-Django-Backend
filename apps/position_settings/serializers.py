"""
岗位设置模块序列化器。

数据库简化重构：
- 适配新的 Position 模型结构
- 处理 requirements JSON 的序列化
- 兼容原 PositionCriteria API 响应格式
"""
from rest_framework import serializers
from .models import Position


class PositionListSerializer(serializers.ModelSerializer):
    """岗位列表序列化器（精简版）。"""
    
    resume_count = serializers.SerializerMethodField()
    # 兼容旧API字段名
    position = serializers.CharField(source='title', read_only=True)
    
    class Meta:
        model = Position
        fields = [
            'id', 'title', 'position', 'department', 'description',
            'is_active', 'resume_count', 'created_at'
        ]
    
    def get_resume_count(self, obj):
        """动态计算简历数量。"""
        return obj.get_resume_count()


class PositionDetailSerializer(serializers.ModelSerializer):
    """岗位详情序列化器（完整版）。"""
    
    resume_count = serializers.SerializerMethodField()
    # 兼容旧API字段名
    position = serializers.CharField(source='title', read_only=True)
    # requirements JSON 展开字段（兼容旧 PositionCriteria）
    required_skills = serializers.SerializerMethodField()
    optional_skills = serializers.SerializerMethodField()
    min_experience = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()
    salary_range = serializers.SerializerMethodField()
    salary_min = serializers.SerializerMethodField()
    salary_max = serializers.SerializerMethodField()
    project_requirements = serializers.SerializerMethodField()
    
    class Meta:
        model = Position
        fields = [
            'id', 'created_at', 'updated_at',
            'title', 'position', 'department', 'description',
            'requirements',
            # 展开的兼容字段
            'required_skills', 'optional_skills', 'min_experience',
            'education', 'certifications', 'salary_range',
            'salary_min', 'salary_max', 'project_requirements',
            'is_active', 'resume_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_resume_count(self, obj):
        """动态计算简历数量。"""
        return obj.get_resume_count()
    
    def get_required_skills(self, obj):
        """从 requirements JSON 提取必备技能。"""
        return (obj.requirements or {}).get('required_skills', [])
    
    def get_optional_skills(self, obj):
        """从 requirements JSON 提取可选技能。"""
        return (obj.requirements or {}).get('optional_skills', [])
    
    def get_min_experience(self, obj):
        """从 requirements JSON 提取最低工作经验。"""
        return (obj.requirements or {}).get('min_experience', 0)
    
    def get_education(self, obj):
        """从 requirements JSON 提取学历要求。"""
        return (obj.requirements or {}).get('education', [])
    
    def get_certifications(self, obj):
        """从 requirements JSON 提取证书要求。"""
        return (obj.requirements or {}).get('certifications', [])
    
    def get_salary_range(self, obj):
        """从 requirements JSON 提取薪资范围。"""
        return (obj.requirements or {}).get('salary_range', [0, 0])
    
    def get_salary_min(self, obj):
        """从 requirements JSON 提取最低薪资。"""
        salary_range = (obj.requirements or {}).get('salary_range', [0, 0])
        return salary_range[0] if len(salary_range) > 0 else 0
    
    def get_salary_max(self, obj):
        """从 requirements JSON 提取最高薪资。"""
        salary_range = (obj.requirements or {}).get('salary_range', [0, 0])
        return salary_range[1] if len(salary_range) > 1 else 0
    
    def get_project_requirements(self, obj):
        """从 requirements JSON 提取项目要求。"""
        return (obj.requirements or {}).get('project_requirements', {})


class PositionCreateSerializer(serializers.ModelSerializer):
    """岗位创建序列化器（支持旧格式）。"""
    
    # 支持旧API字段名
    position = serializers.CharField(required=False, write_only=True)
    # 展开字段（写入时合并到 requirements）
    required_skills = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    optional_skills = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    min_experience = serializers.IntegerField(required=False, write_only=True)
    education = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    certifications = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    salary_min = serializers.IntegerField(required=False, write_only=True)
    salary_max = serializers.IntegerField(required=False, write_only=True)
    project_requirements = serializers.DictField(required=False, write_only=True)
    
    class Meta:
        model = Position
        fields = [
            'title', 'position', 'department', 'description',
            'requirements', 'is_active',
            # 展开字段
            'required_skills', 'optional_skills', 'min_experience',
            'education', 'certifications', 'salary_min', 'salary_max',
            'project_requirements'
        ]
    
    def validate(self, data):
        """合并展开字段到 requirements JSON。"""
        # 处理 position -> title 兼容
        if 'position' in data and 'title' not in data:
            data['title'] = data.pop('position')
        elif 'position' in data:
            data.pop('position')
        
        # 合并展开字段到 requirements
        requirements = data.get('requirements', {})
        if not requirements:
            requirements = {}
        
        field_mapping = {
            'required_skills': 'required_skills',
            'optional_skills': 'optional_skills',
            'min_experience': 'min_experience',
            'education': 'education',
            'certifications': 'certifications',
            'project_requirements': 'project_requirements',
        }
        
        for input_field, req_field in field_mapping.items():
            if input_field in data:
                requirements[req_field] = data.pop(input_field)
        
        # 处理薪资范围
        if 'salary_min' in data or 'salary_max' in data:
            salary_min = data.pop('salary_min', 0)
            salary_max = data.pop('salary_max', 0)
            requirements['salary_range'] = [salary_min, salary_max]
        
        if requirements:
            data['requirements'] = requirements
        
        return data
    
    def create(self, validated_data):
        """创建岗位。"""
        return Position.objects.create(**validated_data)


class PositionUpdateSerializer(serializers.ModelSerializer):
    """岗位更新序列化器。"""
    
    # 支持旧API字段名
    position = serializers.CharField(required=False, write_only=True)
    # 展开字段
    required_skills = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    optional_skills = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    min_experience = serializers.IntegerField(required=False, write_only=True)
    education = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    certifications = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    salary_min = serializers.IntegerField(required=False, write_only=True)
    salary_max = serializers.IntegerField(required=False, write_only=True)
    project_requirements = serializers.DictField(required=False, write_only=True)
    
    class Meta:
        model = Position
        fields = [
            'title', 'position', 'department', 'description',
            'requirements', 'is_active',
            # 展开字段
            'required_skills', 'optional_skills', 'min_experience',
            'education', 'certifications', 'salary_min', 'salary_max',
            'project_requirements'
        ]
    
    def validate(self, data):
        """合并展开字段到 requirements JSON。"""
        # 处理 position -> title 兼容
        if 'position' in data:
            if 'title' not in data:
                data['title'] = data.pop('position')
            else:
                data.pop('position')
        
        # 获取现有 requirements 或新的
        requirements = data.get('requirements')
        if requirements is None and self.instance:
            requirements = dict(self.instance.requirements or {})
        elif requirements is None:
            requirements = {}
        
        field_mapping = {
            'required_skills': 'required_skills',
            'optional_skills': 'optional_skills',
            'min_experience': 'min_experience',
            'education': 'education',
            'certifications': 'certifications',
            'project_requirements': 'project_requirements',
        }
        
        for input_field, req_field in field_mapping.items():
            if input_field in data:
                requirements[req_field] = data.pop(input_field)
        
        # 处理薪资范围
        if 'salary_min' in data or 'salary_max' in data:
            current_range = requirements.get('salary_range', [0, 0])
            salary_min = data.pop('salary_min', current_range[0] if len(current_range) > 0 else 0)
            salary_max = data.pop('salary_max', current_range[1] if len(current_range) > 1 else 0)
            requirements['salary_range'] = [salary_min, salary_max]
        
        data['requirements'] = requirements
        
        return data


class ResumeAssignmentSerializer(serializers.Serializer):
    """简历分配到岗位序列化器。"""
    
    resume_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="要分配的简历ID列表"
    )


# 兼容旧API的别名
PositionCriteriaSerializer = PositionDetailSerializer
PositionCriteriaListSerializer = PositionListSerializer
