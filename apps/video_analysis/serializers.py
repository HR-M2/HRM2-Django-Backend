"""
视频分析模块序列化器。

数据库简化重构：
- 关联到 Resume（原 ResumeData）
- 处理 analysis_result JSON 的序列化
- 从 resume 关联获取 candidate_name, position_applied
"""
from rest_framework import serializers
from .models import VideoAnalysis


class VideoAnalysisSerializer(serializers.ModelSerializer):
    """VideoAnalysis 模型序列化器（完整版）。"""
    
    # 从关联获取的字段（兼容旧API）
    candidate_name = serializers.SerializerMethodField()
    position_applied = serializers.SerializerMethodField()
    resume_file_hash = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    # analysis_result JSON 展开字段
    personality = serializers.SerializerMethodField()
    fraud_score = serializers.SerializerMethodField()
    confidence_score = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoAnalysis
        fields = [
            'id', 'created_at', 'resume',
            'video_file', 'video_name',
            'status', 'status_display', 'error_message',
            'analysis_result',
            # 展开字段
            'personality', 'fraud_score', 'confidence_score', 'summary',
            # 兼容旧API
            'candidate_name', 'position_applied', 'resume_file_hash'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_candidate_name(self, obj):
        """从关联简历获取候选人姓名。"""
        return obj.candidate_name
    
    def get_position_applied(self, obj):
        """从关联简历获取应聘岗位。"""
        return obj.position_applied
    
    def get_resume_file_hash(self, obj):
        """从关联简历获取文件哈希。"""
        return obj.resume.file_hash if obj.resume else None
    
    def get_status_display(self, obj):
        """返回状态的显示名称。"""
        return obj.get_status_display()
    
    def get_personality(self, obj):
        """从 analysis_result JSON 提取人格分析。"""
        if obj.analysis_result:
            return obj.analysis_result.get('personality')
        return None
    
    def get_fraud_score(self, obj):
        """从 analysis_result JSON 提取欺诈分数。"""
        if obj.analysis_result:
            return obj.analysis_result.get('fraud_score')
        return None
    
    def get_confidence_score(self, obj):
        """从 analysis_result JSON 提取置信度分数。"""
        if obj.analysis_result:
            return obj.analysis_result.get('confidence_score')
        return None
    
    def get_summary(self, obj):
        """从 analysis_result JSON 提取摘要。"""
        if obj.analysis_result:
            return obj.analysis_result.get('summary')
        return None


class VideoAnalysisListSerializer(serializers.ModelSerializer):
    """VideoAnalysis 列表序列化器（精简版）。"""
    
    candidate_name = serializers.SerializerMethodField()
    position_applied = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoAnalysis
        fields = [
            'id', 'created_at', 'resume',
            'video_name', 'status', 'status_display',
            'candidate_name', 'position_applied'
        ]
    
    def get_candidate_name(self, obj):
        """从关联简历获取候选人姓名。"""
        return obj.candidate_name
    
    def get_position_applied(self, obj):
        """从关联简历获取应聘岗位。"""
        return obj.position_applied
    
    def get_status_display(self, obj):
        """返回状态的显示名称。"""
        return obj.get_status_display()


class VideoAnalysisCreateSerializer(serializers.ModelSerializer):
    """VideoAnalysis 创建序列化器。"""
    
    # 支持旧API格式
    candidate_name = serializers.CharField(required=False, write_only=True)
    position_applied = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = VideoAnalysis
        fields = [
            'resume', 'video_file', 'video_name',
            # 旧API兼容字段（会被忽略）
            'candidate_name', 'position_applied'
        ]
    
    def validate(self, data):
        """验证并清理旧API字段。"""
        # 移除旧API字段（这些信息从 resume 关联获取）
        data.pop('candidate_name', None)
        data.pop('position_applied', None)
        
        if 'resume' not in data:
            raise serializers.ValidationError("必须提供 resume（简历ID）")
        
        return data


class VideoAnalysisUpdateSerializer(serializers.ModelSerializer):
    """VideoAnalysis 更新序列化器。"""
    
    class Meta:
        model = VideoAnalysis
        fields = ['status', 'error_message', 'analysis_result']
    
    def validate_status(self, value):
        """验证状态值有效性。"""
        valid_statuses = [choice[0] for choice in VideoAnalysis.Status.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"无效的状态值，有效值：{valid_statuses}")
        return value


class VideoAnalysisResultSerializer(serializers.Serializer):
    """视频分析结果序列化器（用于接收分析结果）。"""
    
    personality = serializers.DictField(required=False, help_text="人格分析结果")
    fraud_score = serializers.FloatField(required=False, help_text="欺诈分数")
    confidence_score = serializers.FloatField(required=False, help_text="置信度分数")
    summary = serializers.CharField(required=False, help_text="分析摘要")
    
    # 兼容旧API：独立字段
    neuroticism_score = serializers.FloatField(required=False)
    extraversion_score = serializers.FloatField(required=False)
    openness_score = serializers.FloatField(required=False)
    agreeableness_score = serializers.FloatField(required=False)
    conscientiousness_score = serializers.FloatField(required=False)
    
    def to_internal_value(self, data):
        """将旧格式转换为新格式。"""
        result = super().to_internal_value(data)
        
        # 如果提供了独立的人格分数字段，合并到 personality
        personality_fields = [
            'neuroticism_score', 'extraversion_score', 'openness_score',
            'agreeableness_score', 'conscientiousness_score'
        ]
        
        if any(f in result for f in personality_fields):
            personality = result.get('personality', {})
            field_mapping = {
                'neuroticism_score': 'neuroticism',
                'extraversion_score': 'extraversion',
                'openness_score': 'openness',
                'agreeableness_score': 'agreeableness',
                'conscientiousness_score': 'conscientiousness',
            }
            for old_field, new_field in field_mapping.items():
                if old_field in result:
                    personality[new_field] = result.pop(old_field)
            result['personality'] = personality
        
        return result
