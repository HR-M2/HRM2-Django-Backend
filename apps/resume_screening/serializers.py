"""
简历筛选模块序列化器。

数据库简化重构：
- ScreeningTask 适配新的简化模型
- 删除 ScreeningReport, ResumeData 序列化器（模型已删除）
- 保留兼容旧 API 的字段
"""
from rest_framework import serializers
from .models import ScreeningTask


class ScreeningTaskSerializer(serializers.ModelSerializer):
    """ScreeningTask 模型序列化器（简化版）。"""
    
    position_title = serializers.SerializerMethodField()
    position_data = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    # 兼容旧API字段（计算值）
    current_step = serializers.SerializerMethodField()
    total_steps = serializers.SerializerMethodField()
    
    class Meta:
        model = ScreeningTask
        fields = [
            'id', 'created_at', 'status', 'status_display',
            'progress', 'total_count', 'processed_count',
            'error_message', 'position', 'position_title', 'position_data',
            # 兼容旧API
            'current_step', 'total_steps'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_position_title(self, obj):
        """返回关联岗位名称。"""
        return obj.position.title if obj.position else None
    
    def get_position_data(self, obj):
        """返回关联岗位详情（兼容旧 API）。"""
        if obj.position:
            return obj.position.to_dict()
        return None
    
    def get_status_display(self, obj):
        """返回状态的显示名称。"""
        return obj.get_status_display()
    
    def get_current_step(self, obj):
        """兼容旧 API：当前步骤 = 已处理数量。"""
        return obj.processed_count
    
    def get_total_steps(self, obj):
        """兼容旧 API：总步骤 = 总数量。"""
        return obj.total_count


class ScreeningTaskListSerializer(serializers.ModelSerializer):
    """ScreeningTask 列表序列化器（精简版）。"""
    
    position_title = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ScreeningTask
        fields = [
            'id', 'created_at', 'status', 'status_display',
            'progress', 'total_count', 'processed_count',
            'position', 'position_title'
        ]
    
    def get_position_title(self, obj):
        """返回关联岗位名称。"""
        return obj.position.title if obj.position else None
    
    def get_status_display(self, obj):
        """返回状态的显示名称。"""
        return obj.get_status_display()


class ScreeningTaskCreateSerializer(serializers.ModelSerializer):
    """ScreeningTask 创建序列化器。"""
    
    # 支持旧API格式：传入 position_data 字典
    position_data = serializers.DictField(required=False, write_only=True)
    
    class Meta:
        model = ScreeningTask
        fields = ['position', 'position_data', 'total_count']
    
    def validate(self, data):
        """验证岗位信息。"""
        # 必须提供 position 或 position_data
        if 'position' not in data and 'position_data' not in data:
            raise serializers.ValidationError("必须提供岗位信息（position 或 position_data）")
        
        # 如果提供了 position_data，忽略它（需要在 View 中处理创建/查找 Position）
        if 'position_data' in data:
            data.pop('position_data')
        
        return data


class ResumeScreeningInputSerializer(serializers.Serializer):
    """简历筛选输入序列化器（批量筛选）。"""
    
    position = serializers.DictField(required=False, help_text="岗位信息（旧格式）")
    position_id = serializers.UUIDField(required=False, help_text="岗位ID（新格式）")
    resumes = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="简历列表（旧格式）"
    )
    resume_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="简历ID列表（新格式）"
    )
    
    def validate(self, data):
        """验证输入数据。"""
        # 必须提供岗位信息
        if 'position' not in data and 'position_id' not in data:
            raise serializers.ValidationError("必须提供岗位信息（position 或 position_id）")
        
        # 必须提供简历信息
        if 'resumes' not in data and 'resume_ids' not in data:
            raise serializers.ValidationError("必须提供简历信息（resumes 或 resume_ids）")
        
        return data
    
    def validate_resumes(self, value):
        """验证旧格式简历列表。"""
        if not value:
            return value
        
        for idx, resume in enumerate(value):
            if 'content' not in resume:
                raise serializers.ValidationError(f"第{idx}份简历缺少content字段")
        
        return value



