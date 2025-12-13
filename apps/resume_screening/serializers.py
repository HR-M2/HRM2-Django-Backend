"""
简历筛选模块序列化器。
"""
from rest_framework import serializers
from .models import ResumeScreeningTask, ScreeningReport, ResumeData


class ResumeScreeningTaskSerializer(serializers.ModelSerializer):
    """ResumeScreeningTask模型序列化器。"""
    
    class Meta:
        model = ResumeScreeningTask
        fields = [
            'id', 'created_at', 'status', 
            'progress', 'current_step', 'total_steps',
            'error_message', 'current_speaker', 'position_data'
        ]
        read_only_fields = ['id', 'created_at']


class ScreeningReportSerializer(serializers.ModelSerializer):
    """ScreeningReport模型序列化器。"""
    
    class Meta:
        model = ScreeningReport
        fields = [
            'id', 'task', 'created_at', 'md_file', 
            'original_filename', 'resume_content', 'json_report_content'
        ]
        read_only_fields = ['id', 'created_at']


class ResumeDataSerializer(serializers.ModelSerializer):
    """ResumeData模型序列化器。"""
    
    video_analysis_id = serializers.SerializerMethodField()
    
    class Meta:
        model = ResumeData
        fields = [
            'id', 'created_at', 'position_title',
            'position_details', 'candidate_name', 'resume_content',
            'screening_score', 'screening_summary', 'resume_file_hash',
            'report_md_file', 'report_json_file', 'json_report_content',
            'task', 'report', 'group', 'video_analysis_id'
        ]
        read_only_fields = ['id', 'created_at', 'resume_file_hash']
    
    def get_video_analysis_id(self, obj):
        if obj.video_analysis:
            return str(obj.video_analysis.id)
        return None


class ResumeScreeningInputSerializer(serializers.Serializer):
    """简历筛选输入序列化器。"""
    
    position = serializers.DictField(required=True, help_text="岗位信息")
    resumes = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="简历列表"
    )
    
    def validate_position(self, value):
        if not value:
            raise serializers.ValidationError("岗位信息不能为空")
        return value
    
    def validate_resumes(self, value):
        if not value:
            raise serializers.ValidationError("简历列表不能为空")
        
        for idx, resume in enumerate(value):
            if 'content' not in resume:
                raise serializers.ValidationError(f"第{idx}份简历缺少content字段")
        
        return value


