"""
最终推荐模块序列化器。

数据库简化重构：
- ComprehensiveAnalysis 适配新模型
- 处理 recommendation JSON 的序列化
- 删除废弃模型（InterviewEvaluationTask）的 serializer
- 兼容原 CandidateComprehensiveAnalysis API 响应格式
"""
from rest_framework import serializers
from .models import ComprehensiveAnalysis


class ComprehensiveAnalysisSerializer(serializers.ModelSerializer):
    """ComprehensiveAnalysis 模型序列化器（完整版）。"""
    
    # 从关联获取的字段
    candidate_name = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    resume_content = serializers.SerializerMethodField()
    
    # recommendation JSON 展开字段（兼容旧API）
    recommendation_level = serializers.SerializerMethodField()
    recommendation_label = serializers.SerializerMethodField()
    recommendation_action = serializers.SerializerMethodField()
    
    # 兼容旧字段名
    comprehensive_report = serializers.CharField(source='report', read_only=True)
    
    class Meta:
        model = ComprehensiveAnalysis
        fields = [
            'id', 'created_at', 'resume',
            'final_score', 'recommendation', 'dimension_scores', 'report',
            # 展开字段（兼容旧API）
            'recommendation_level', 'recommendation_label', 'recommendation_action',
            # 兼容旧字段名
            'comprehensive_report',
            # 从关联获取
            'candidate_name', 'position_title', 'resume_content'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_candidate_name(self, obj):
        """从关联简历获取候选人姓名。"""
        return obj.resume.candidate_name if obj.resume else None
    
    def get_position_title(self, obj):
        """从关联简历获取岗位名称。"""
        if obj.resume and obj.resume.position:
            return obj.resume.position.title
        return None
    
    def get_resume_content(self, obj):
        """从关联简历获取简历内容。"""
        return obj.resume.content if obj.resume else None
    
    def get_recommendation_level(self, obj):
        """从 recommendation JSON 提取推荐等级。"""
        return obj.recommendation_level
    
    def get_recommendation_label(self, obj):
        """从 recommendation JSON 提取推荐标签。"""
        return obj.recommendation_label
    
    def get_recommendation_action(self, obj):
        """从 recommendation JSON 提取推荐行动。"""
        return obj.recommendation_action


class ComprehensiveAnalysisListSerializer(serializers.ModelSerializer):
    """ComprehensiveAnalysis 列表序列化器（精简版）。"""
    
    candidate_name = serializers.SerializerMethodField()
    position_title = serializers.SerializerMethodField()
    recommendation_level = serializers.SerializerMethodField()
    recommendation_label = serializers.SerializerMethodField()
    
    class Meta:
        model = ComprehensiveAnalysis
        fields = [
            'id', 'created_at', 'resume',
            'final_score', 'recommendation_level', 'recommendation_label',
            'candidate_name', 'position_title'
        ]
    
    def get_candidate_name(self, obj):
        """从关联简历获取候选人姓名。"""
        return obj.resume.candidate_name if obj.resume else None
    
    def get_position_title(self, obj):
        """从关联简历获取岗位名称。"""
        if obj.resume and obj.resume.position:
            return obj.resume.position.title
        return None
    
    def get_recommendation_level(self, obj):
        """从 recommendation JSON 提取推荐等级。"""
        return obj.recommendation_level
    
    def get_recommendation_label(self, obj):
        """从 recommendation JSON 提取推荐标签。"""
        return obj.recommendation_label


class ComprehensiveAnalysisCreateSerializer(serializers.ModelSerializer):
    """ComprehensiveAnalysis 创建序列化器。"""
    
    # 支持旧API格式：独立字段
    recommendation_level = serializers.CharField(required=False, write_only=True)
    recommendation_label = serializers.CharField(required=False, write_only=True)
    recommendation_action = serializers.CharField(required=False, write_only=True)
    # 兼容旧字段名
    comprehensive_report = serializers.CharField(required=False, write_only=True)
    # 兼容旧API：resume_data -> resume
    resume_data = serializers.UUIDField(required=False, write_only=True)
    
    class Meta:
        model = ComprehensiveAnalysis
        fields = [
            'resume', 'resume_data',
            'final_score', 'recommendation', 'dimension_scores', 'report',
            # 旧API兼容字段
            'recommendation_level', 'recommendation_label', 'recommendation_action',
            'comprehensive_report'
        ]
    
    def validate(self, data):
        """验证并合并旧API字段。"""
        # 兼容旧API：resume_data -> resume
        if 'resume_data' in data and 'resume' not in data:
            data['resume_id'] = data.pop('resume_data')
        elif 'resume_data' in data:
            data.pop('resume_data')
        
        # 兼容旧API：comprehensive_report -> report
        if 'comprehensive_report' in data and 'report' not in data:
            data['report'] = data.pop('comprehensive_report')
        elif 'comprehensive_report' in data:
            data.pop('comprehensive_report')
        
        # 合并独立字段到 recommendation JSON
        recommendation = data.get('recommendation', {})
        if not recommendation:
            recommendation = {}
        
        if 'recommendation_level' in data:
            recommendation['level'] = data.pop('recommendation_level')
        if 'recommendation_label' in data:
            recommendation['label'] = data.pop('recommendation_label')
        if 'recommendation_action' in data:
            recommendation['action'] = data.pop('recommendation_action')
        
        if recommendation:
            data['recommendation'] = recommendation
        
        # 验证必填字段
        if 'resume' not in data and 'resume_id' not in data:
            raise serializers.ValidationError("必须提供 resume（简历ID）")
        
        return data


class ComprehensiveAnalysisUpdateSerializer(serializers.ModelSerializer):
    """ComprehensiveAnalysis 更新序列化器。"""
    
    # 支持旧API格式
    recommendation_level = serializers.CharField(required=False, write_only=True)
    recommendation_label = serializers.CharField(required=False, write_only=True)
    recommendation_action = serializers.CharField(required=False, write_only=True)
    comprehensive_report = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = ComprehensiveAnalysis
        fields = [
            'final_score', 'recommendation', 'dimension_scores', 'report',
            'recommendation_level', 'recommendation_label', 'recommendation_action',
            'comprehensive_report'
        ]
    
    def validate(self, data):
        """验证并合并旧API字段。"""
        # 兼容旧API：comprehensive_report -> report
        if 'comprehensive_report' in data:
            if 'report' not in data:
                data['report'] = data.pop('comprehensive_report')
            else:
                data.pop('comprehensive_report')
        
        # 合并独立字段到 recommendation JSON
        recommendation = data.get('recommendation')
        if recommendation is None and self.instance:
            recommendation = dict(self.instance.recommendation or {})
        elif recommendation is None:
            recommendation = {}
        
        if 'recommendation_level' in data:
            recommendation['level'] = data.pop('recommendation_level')
        if 'recommendation_label' in data:
            recommendation['label'] = data.pop('recommendation_label')
        if 'recommendation_action' in data:
            recommendation['action'] = data.pop('recommendation_action')
        
        data['recommendation'] = recommendation
        
        return data


class RecommendationInputSerializer(serializers.Serializer):
    """综合分析输入序列化器。"""
    
    resume_id = serializers.UUIDField(required=True, help_text="简历ID")
    # 可选：指定要包含的数据源
    include_screening = serializers.BooleanField(default=True, help_text="是否包含筛选结果")
    include_video = serializers.BooleanField(default=True, help_text="是否包含视频分析")
    include_interview = serializers.BooleanField(default=True, help_text="是否包含面试记录")


