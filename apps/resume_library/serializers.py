"""
简历库模块序列化器。
"""
from rest_framework import serializers
from .models import ResumeLibrary


class ResumeLibrarySerializer(serializers.ModelSerializer):
    """ResumeLibrary模型序列化器。"""
    
    content_preview = serializers.SerializerMethodField()
    file_hash_short = serializers.SerializerMethodField()
    
    class Meta:
        model = ResumeLibrary
        fields = [
            'id', 'created_at', 'updated_at',
            'filename', 'file_hash', 'file_hash_short',
            'file_size', 'file_type', 'content', 'content_preview',
            'candidate_name', 'is_screened', 'is_assigned', 'notes'
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


class ResumeLibraryListSerializer(serializers.ModelSerializer):
    """简历库列表序列化器（精简版）。"""
    
    content_preview = serializers.SerializerMethodField()
    file_hash_short = serializers.SerializerMethodField()
    
    class Meta:
        model = ResumeLibrary
        fields = [
            'id', 'filename', 'file_hash_short', 'file_size', 'file_type',
            'candidate_name', 'is_screened', 'is_assigned', 'notes',
            'created_at', 'content_preview'
        ]
    
    def get_content_preview(self, obj):
        """返回简历内容预览（前200字符）。"""
        if obj.content and len(obj.content) > 200:
            return obj.content[:200] + '...'
        return obj.content
    
    def get_file_hash_short(self, obj):
        """返回文件哈希值的前8位。"""
        return obj.file_hash[:8] if obj.file_hash else ''


class ResumeUploadSerializer(serializers.Serializer):
    """简历上传请求序列化器。"""
    
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
