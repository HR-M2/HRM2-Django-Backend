"""
面试辅助模块序列化器。

数据库简化重构：
- InterviewSession 适配新模型
- 从 resume.position 获取岗位配置
- 兼容原 InterviewAssistSession API 响应格式
"""
from rest_framework import serializers
from .models import InterviewSession


class InterviewSessionSerializer(serializers.ModelSerializer):
    """InterviewSession 模型序列化器（完整版）。"""
    
    # 从关联获取的字段
    candidate_name = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    job_config = serializers.SerializerMethodField()
    resume_content = serializers.SerializerMethodField()
    
    # 计算字段
    current_round = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewSession
        fields = [
            'id', 'created_at', 'updated_at', 'resume',
            'qa_records', 'final_report',
            # 从关联获取
            'candidate_name', 'position_title', 'job_config', 'resume_content',
            # 计算字段
            'current_round', 'is_completed'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_candidate_name(self, obj):
        """从关联简历获取候选人姓名。"""
        return obj.resume.candidate_name if obj.resume else None
    
    def get_position_title(self, obj):
        """从关联简历获取岗位名称。"""
        if obj.resume and obj.resume.position:
            return obj.resume.position.title
        return None
    
    def get_job_config(self, obj):
        """从关联简历获取岗位配置（兼容旧API）。"""
        return obj.job_config
    
    def get_resume_content(self, obj):
        """从关联简历获取简历内容。"""
        return obj.resume.content if obj.resume else None
    
    def get_current_round(self, obj):
        """返回当前轮次。"""
        return obj.current_round
    
    def get_is_completed(self, obj):
        """返回是否已完成。"""
        return obj.is_completed


class InterviewSessionListSerializer(serializers.ModelSerializer):
    """InterviewSession 列表序列化器（精简版）。"""
    
    candidate_name = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    current_round = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewSession
        fields = [
            'id', 'created_at', 'updated_at', 'resume',
            'candidate_name', 'position_title',
            'current_round', 'is_completed'
        ]
    
    def get_candidate_name(self, obj):
        """从关联简历获取候选人姓名。"""
        return obj.resume.candidate_name if obj.resume else None
    
    def get_position_title(self, obj):
        """从关联简历获取岗位名称。"""
        if obj.resume and obj.resume.position:
            return obj.resume.position.title
        return None
    
    def get_current_round(self, obj):
        """返回当前轮次。"""
        return obj.current_round
    
    def get_is_completed(self, obj):
        """返回是否已完成。"""
        return obj.is_completed


class InterviewSessionCreateSerializer(serializers.ModelSerializer):
    """InterviewSession 创建序列化器。"""
    
    # 支持旧API格式
    resume_data = serializers.UUIDField(required=False, write_only=True)
    job_config = serializers.DictField(required=False, write_only=True)
    
    class Meta:
        model = InterviewSession
        fields = ['resume', 'resume_data', 'job_config']
    
    def validate(self, data):
        """验证并处理旧API字段。"""
        # 兼容旧API：resume_data -> resume
        if 'resume_data' in data and 'resume' not in data:
            data['resume_id'] = data.pop('resume_data')
        elif 'resume_data' in data:
            data.pop('resume_data')
        
        # job_config 不再存储，从 resume.position 获取
        data.pop('job_config', None)
        
        if 'resume' not in data and 'resume_id' not in data:
            raise serializers.ValidationError("必须提供 resume（简历ID）")
        
        return data


class QARecordSerializer(serializers.Serializer):
    """问答记录序列化器。"""
    
    round = serializers.IntegerField(read_only=True)
    question = serializers.CharField()
    answer = serializers.CharField(required=False, allow_blank=True)
    evaluation = serializers.DictField(required=False)


class AddQARecordSerializer(serializers.Serializer):
    """添加问答记录序列化器。"""
    
    question = serializers.CharField(required=True, help_text="面试问题")
    answer = serializers.CharField(required=False, allow_blank=True, help_text="候选人回答")
    evaluation = serializers.DictField(required=False, help_text="评估结果")


class FinalReportSerializer(serializers.Serializer):
    """最终报告序列化器。"""
    
    overall_score = serializers.FloatField(required=False, help_text="总体评分")
    strengths = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="优势"
    )
    weaknesses = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="不足"
    )
    recommendation = serializers.CharField(required=False, help_text="推荐意见")
    summary = serializers.CharField(required=False, help_text="总结")


class SetFinalReportSerializer(serializers.Serializer):
    """设置最终报告序列化器。"""
    
    report = serializers.DictField(required=True, help_text="面试报告内容")


