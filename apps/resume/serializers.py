"""
简历管理模块序列化器。

数据库简化重构：
- 合并原 ResumeLibrary 和 ResumeData 的序列化器
- 兼容原 API 响应格式
"""
from rest_framework import serializers
from .models import Resume


class ResumeListSerializer(serializers.ModelSerializer):
    """简历列表序列化器（精简版）。"""
    
    content_preview = serializers.SerializerMethodField()
    file_hash_short = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    # 兼容旧API字段
    is_screened = serializers.SerializerMethodField()
    is_assigned = serializers.SerializerMethodField()
    
    class Meta:
        model = Resume
        fields = [
            'id', 'filename', 'file_hash_short', 'file_size', 'file_type',
            'candidate_name', 'status', 'status_display',
            'position', 'position_title',
            'is_screened', 'is_assigned',
            'notes', 'created_at', 'content_preview'
        ]
    
    def get_content_preview(self, obj):
        """返回简历内容预览（前200字符）。"""
        if obj.content and len(obj.content) > 200:
            return obj.content[:200] + '...'
        return obj.content
    
    def get_file_hash_short(self, obj):
        """返回文件哈希值的前8位。"""
        return obj.file_hash[:8] if obj.file_hash else ''
    
    def get_position_title(self, obj):
        """返回关联岗位名称。"""
        return obj.position.title if obj.position else None
    
    def get_status_display(self, obj):
        """返回状态的显示名称。"""
        return obj.get_status_display()
    
    def get_is_screened(self, obj):
        """兼容旧API：是否已筛选。"""
        return obj.status != Resume.Status.PENDING
    
    def get_is_assigned(self, obj):
        """兼容旧API：是否已分配岗位。"""
        return obj.position_id is not None


class ResumeDetailSerializer(serializers.ModelSerializer):
    """简历详情序列化器（完整版）。"""
    
    content_preview = serializers.SerializerMethodField()
    file_hash_short = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    position_details = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    # 兼容旧API字段
    is_screened = serializers.SerializerMethodField()
    is_assigned = serializers.SerializerMethodField()
    # 筛选结果展开字段（兼容旧 ResumeData）
    screening_score = serializers.SerializerMethodField()
    screening_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Resume
        fields = [
            'id', 'created_at', 'updated_at',
            'filename', 'file_hash', 'file_hash_short',
            'file_size', 'file_type', 'content', 'content_preview',
            'candidate_name', 'status', 'status_display',
            'position', 'position_title', 'position_details',
            'is_screened', 'is_assigned',
            'screening_result', 'screening_score', 'screening_summary',
            'screening_report', 'notes'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'file_hash']
    
    def get_content_preview(self, obj):
        """返回简历内容预览（前200字符）。"""
        if obj.content and len(obj.content) > 200:
            return obj.content[:200] + '...'
        return obj.content
    
    def get_file_hash_short(self, obj):
        """返回文件哈希值的前8位。"""
        return obj.file_hash[:8] if obj.file_hash else ''
    
    def get_position_title(self, obj):
        """返回关联岗位名称。"""
        return obj.position.title if obj.position else None
    
    def get_position_details(self, obj):
        """返回关联岗位详情（兼容旧 ResumeData.position_details）。"""
        if obj.position:
            return obj.position.to_dict()
        return None
    
    def get_status_display(self, obj):
        """返回状态的显示名称。"""
        return obj.get_status_display()
    
    def get_is_screened(self, obj):
        """兼容旧API：是否已筛选。"""
        return obj.status != Resume.Status.PENDING
    
    def get_is_assigned(self, obj):
        """兼容旧API：是否已分配岗位。"""
        return obj.position_id is not None
    
    def get_screening_score(self, obj):
        """从 screening_result JSON 提取筛选分数。"""
        if obj.screening_result:
            return obj.screening_result.get('score')
        return None
    
    def get_screening_summary(self, obj):
        """从 screening_result JSON 提取筛选摘要。"""
        if obj.screening_result:
            return obj.screening_result.get('summary')
        return None


class ResumeCreateSerializer(serializers.ModelSerializer):
    """简历创建序列化器。"""
    
    class Meta:
        model = Resume
        fields = [
            'filename', 'file_hash', 'file_size', 'file_type',
            'candidate_name', 'content', 'position', 'notes'
        ]
    
    def validate_file_hash(self, value):
        """验证文件哈希唯一性。"""
        if Resume.objects.filter(file_hash=value).exists():
            raise serializers.ValidationError("该简历已存在（文件哈希重复）")
        return value


class ResumeUpdateSerializer(serializers.ModelSerializer):
    """简历更新序列化器。"""
    
    class Meta:
        model = Resume
        fields = [
            'candidate_name', 'position', 'status', 'notes',
            'screening_result', 'screening_report'
        ]
    
    def validate_status(self, value):
        """验证状态值有效性。"""
        valid_statuses = [choice[0] for choice in Resume.Status.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"无效的状态值，有效值：{valid_statuses}")
        return value


class ResumeUploadSerializer(serializers.Serializer):
    """简历上传请求序列化器（批量）。"""
    
    resumes = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="简历列表，每项包含 name, content, metadata"
    )
    
    def validate_resumes(self, value):
        if not value:
            raise serializers.ValidationError("至少需要上传一份简历")
        if len(value) > 50:
            raise serializers.ValidationError("单次最多上传50份简历")
        return value


class BatchDeleteSerializer(serializers.Serializer):
    """批量删除请求序列化器。"""
    
    resume_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="要删除的简历ID列表"
    )


class CheckHashSerializer(serializers.Serializer):
    """检查哈希值请求序列化器。"""
    
    hashes = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="要检查的哈希值列表"
    )


class ResumeAssignSerializer(serializers.Serializer):
    """简历分配岗位序列化器。"""
    
    resume_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="要分配的简历ID列表"
    )
    position_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="目标岗位ID，为空则取消分配"
    )


# 兼容旧API的别名
ResumeLibrarySerializer = ResumeDetailSerializer
ResumeLibraryListSerializer = ResumeListSerializer
