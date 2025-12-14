"""
OpenAPI Schema 定义模块。

提供统一的响应 Schema 包装器和常用 Schema 定义，
用于 drf-spectacular 的 @extend_schema 装饰器。
"""
from rest_framework import serializers
from drf_spectacular.utils import inline_serializer, OpenApiExample


# =============================================================================
# 基础响应包装器
# =============================================================================

def api_response(data_schema, name: str, description: str = ""):
    """
    生成统一的 API 响应 Schema: {code, message, data}
    
    Args:
        data_schema: 数据字段的 Serializer 或 serializers.Field
        name: Schema 名称前缀
        description: 响应描述
    
    Returns:
        inline_serializer 实例
    """
    return inline_serializer(
        name=f'Api{name}Resp',
        fields={
            'code': serializers.IntegerField(default=200, help_text="状态码"),
            'message': serializers.CharField(default="成功", help_text="消息"),
            'data': data_schema,
        }
    )


def paginated_response(item_schema, name: str):
    """
    生成分页响应 Schema: {code, message, data: {items, total, page, page_size}}
    
    Args:
        item_schema: 列表项的 Serializer
        name: Schema 名称前缀
    
    Returns:
        inline_serializer 实例
    """
    return api_response(
        data_schema=inline_serializer(
            name=f'{name}PaginatedData',
            fields={
                'items': serializers.ListSerializer(child=item_schema),
                'total': serializers.IntegerField(help_text="总数"),
                'page': serializers.IntegerField(help_text="当前页"),
                'page_size': serializers.IntegerField(help_text="每页数量"),
            }
        ),
        name=f'{name}Paginated'
    )


def list_response(item_schema, name: str, list_field: str = "items"):
    """
    生成列表响应 Schema（非分页）
    
    Args:
        item_schema: 列表项的 Serializer
        name: Schema 名称前缀
        list_field: 列表字段名
    
    Returns:
        inline_serializer 实例
    """
    return api_response(
        data_schema=inline_serializer(
            name=f'{name}ListData',
            fields={
                list_field: serializers.ListSerializer(child=item_schema),
                'total': serializers.IntegerField(help_text="总数"),
            }
        ),
        name=f'{name}List'
    )


def success_response(name: str = "Success"):
    """生成简单成功响应 Schema（无 data 或 data 为 null）"""
    return inline_serializer(
        name=f'{name}Response',
        fields={
            'code': serializers.IntegerField(default=200),
            'message': serializers.CharField(default="成功"),
            'data': serializers.JSONField(allow_null=True, default=None),
        }
    )


def error_response(name: str = "Error"):
    """生成错误响应 Schema"""
    return inline_serializer(
        name=f'{name}Response',
        fields={
            'code': serializers.IntegerField(help_text="错误码"),
            'message': serializers.CharField(help_text="错误消息"),
            'data': serializers.JSONField(allow_null=True, default=None),
        }
    )


# =============================================================================
# 通用字段 Schema
# =============================================================================

class IdResponseSerializer(serializers.Serializer):
    """ID 响应"""
    id = serializers.CharField(help_text="记录ID")


# =============================================================================
# 嵌套结构 Schema（替换 JSONField）
# =============================================================================

class ScreeningScoreSerializer(serializers.Serializer):
    """筛选得分结构"""
    hr_score = serializers.FloatField(required=False, allow_null=True, help_text="HR评分")
    technical_score = serializers.FloatField(required=False, allow_null=True, help_text="技术评分")
    manager_score = serializers.FloatField(required=False, allow_null=True, help_text="经理评分")
    comprehensive_score = serializers.FloatField(help_text="综合评分")


class ProjectRequirementsSerializer(serializers.Serializer):
    """项目要求结构"""
    min_projects = serializers.IntegerField(required=False, default=0, help_text="最少项目数")
    team_lead_experience = serializers.BooleanField(required=False, default=False, help_text="是否需要团队领导经验")


class VideoAnalysisResultSerializer(serializers.Serializer):
    """视频分析结果结构"""
    fraud_score = serializers.FloatField(required=False, allow_null=True, help_text="欺诈评分")
    neuroticism_score = serializers.FloatField(required=False, allow_null=True, help_text="神经质评分")
    extraversion_score = serializers.FloatField(required=False, allow_null=True, help_text="外向性评分")
    openness_score = serializers.FloatField(required=False, allow_null=True, help_text="开放性评分")
    agreeableness_score = serializers.FloatField(required=False, allow_null=True, help_text="宜人性评分")
    conscientiousness_score = serializers.FloatField(required=False, allow_null=True, help_text="尽责性评分")


class DimensionScoreDetailSerializer(serializers.Serializer):
    """维度评分详情"""
    dimension_score = serializers.FloatField(help_text="维度得分")
    dimension_name = serializers.CharField(help_text="维度名称")
    weight = serializers.FloatField(help_text="权重")
    strengths = serializers.ListField(child=serializers.CharField(), help_text="优势")
    weaknesses = serializers.ListField(child=serializers.CharField(), help_text="劣势")
    analysis = serializers.CharField(help_text="分析")
    sub_scores = serializers.DictField(child=serializers.FloatField(), help_text="子评分")


class QARecordSerializer(serializers.Serializer):
    """问答记录"""
    question = serializers.CharField(help_text="问题")
    answer = serializers.CharField(help_text="回答")


class OverallAssessmentSerializer(serializers.Serializer):
    """整体评估"""
    recommendation_score = serializers.FloatField(help_text="推荐分数")
    recommendation = serializers.CharField(help_text="推荐结论")
    summary = serializers.CharField(help_text="总结")


class FinalReportSerializer(serializers.Serializer):
    """最终报告结构"""
    overall_assessment = OverallAssessmentSerializer(required=False, help_text="整体评估")
    highlights = serializers.ListField(child=serializers.CharField(), required=False, help_text="亮点")
    red_flags = serializers.ListField(child=serializers.CharField(), required=False, help_text="风险点")


class ResumeSummarySerializer(serializers.Serializer):
    """简历摘要"""
    candidate_name = serializers.CharField(help_text="候选人姓名")
    position_title = serializers.CharField(help_text="应聘岗位")
    screening_score = serializers.FloatField(required=False, allow_null=True, help_text="筛选分数")
    screening_summary = serializers.CharField(required=False, allow_null=True, help_text="筛选摘要")


class InterviewQuestionSerializer(serializers.Serializer):
    """面试问题"""
    question = serializers.CharField(help_text="问题内容")
    category = serializers.CharField(help_text="问题类别")
    difficulty = serializers.IntegerField(help_text="难度等级")
    expected_skills = serializers.ListField(child=serializers.CharField(), help_text="期望技能")
    source = serializers.ChoiceField(
        choices=['resume_based', 'skill_based', 'hr_custom'],
        help_text="问题来源"
    )
    related_point = serializers.CharField(required=False, help_text="相关点")


class DimensionScoreItemSerializer(serializers.Serializer):
    """评估维度评分项"""
    score = serializers.FloatField(help_text="分数")
    comment = serializers.CharField(help_text="评语")


class SkillAssessmentSerializer(serializers.Serializer):
    """技能评估"""
    skill = serializers.CharField(help_text="技能名称")
    level = serializers.CharField(help_text="技能水平")
    evidence = serializers.CharField(help_text="证据")


class AnswerEvaluationSerializer(serializers.Serializer):
    """回答评估结果"""
    normalized_score = serializers.FloatField(help_text="标准化分数")
    dimension_scores = serializers.DictField(
        child=serializers.FloatField(),
        help_text="维度评分（technical_depth, practical_experience, answer_specificity, logical_clarity, honesty, communication）"
    )
    confidence_level = serializers.ChoiceField(
        choices=['genuine', 'uncertain', 'overconfident'],
        help_text="置信度等级"
    )
    should_followup = serializers.BooleanField(help_text="是否需要追问")
    followup_reason = serializers.CharField(required=False, help_text="追问原因")
    feedback = serializers.CharField(help_text="反馈")


class InterviewReportSerializer(serializers.Serializer):
    """面试报告结构"""
    overall_assessment = OverallAssessmentSerializer(help_text="整体评估")
    dimension_analysis = serializers.DictField(
        child=DimensionScoreItemSerializer(),
        help_text="维度分析"
    )
    skill_assessment = SkillAssessmentSerializer(many=True, help_text="技能评估")
    highlights = serializers.ListField(child=serializers.CharField(), help_text="亮点")
    red_flags = serializers.ListField(child=serializers.CharField(), help_text="风险点")
    overconfidence_detected = serializers.BooleanField(help_text="是否检测到过度自信")
    suggested_next_steps = serializers.ListField(child=serializers.CharField(), help_text="建议后续步骤")


class DocumentItemSerializer(serializers.Serializer):
    """参考文档项"""
    name = serializers.CharField(help_text="文档名称")
    content = serializers.CharField(help_text="文档内容")


class QuestionInputSerializer(serializers.Serializer):
    """问题输入"""
    content = serializers.CharField(help_text="问题内容")
    expected_skills = serializers.ListField(
        child=serializers.CharField(), required=False, help_text="期望技能"
    )
    difficulty = serializers.IntegerField(required=False, help_text="难度等级")


class AnswerInputSerializer(serializers.Serializer):
    """回答输入"""
    content = serializers.CharField(help_text="回答内容")


# =============================================================================
# 以下是原有的通用字段 Schema
# =============================================================================


class CountResponseSerializer(serializers.Serializer):
    """计数响应"""
    count = serializers.IntegerField(help_text="数量")


class DeletedCountSerializer(serializers.Serializer):
    """删除计数响应"""
    deleted_count = serializers.IntegerField(help_text="删除数量")


class TaskSubmitSerializer(serializers.Serializer):
    """任务提交响应"""
    status = serializers.CharField(help_text="状态")
    task_id = serializers.CharField(help_text="任务ID")


# =============================================================================
# 视频分析相关 Schema
# =============================================================================

class VideoAnalysisItemSerializer(serializers.Serializer):
    """视频分析项"""
    id = serializers.CharField(help_text="视频分析ID")
    video_name = serializers.CharField(help_text="视频名称")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    position_applied = serializers.CharField(help_text="应聘岗位")
    status = serializers.ChoiceField(
        choices=['pending', 'processing', 'completed', 'failed'],
        help_text="状态"
    )
    confidence_score = serializers.FloatField(allow_null=True, help_text="置信度分数")
    created_at = serializers.DateTimeField(help_text="创建时间")
    analysis_result = VideoAnalysisResultSerializer(required=False, help_text="分析结果")


class VideoAnalysisDetailSerializer(VideoAnalysisItemSerializer):
    """视频分析详情"""
    summary = serializers.CharField(required=False, help_text="分析摘要")
    error_message = serializers.CharField(required=False, help_text="错误信息")
    resume_id = serializers.CharField(required=False, help_text="关联简历ID")


class VideoUploadResponseSerializer(serializers.Serializer):
    """视频上传响应"""
    id = serializers.CharField(help_text="视频分析ID")
    video_name = serializers.CharField(help_text="视频名称")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    position_applied = serializers.CharField(help_text="应聘岗位")
    status = serializers.CharField(help_text="状态")
    created_at = serializers.DateTimeField(help_text="创建时间")
    resume_id = serializers.CharField(required=False, help_text="关联简历ID")


class VideoUpdateResponseSerializer(serializers.Serializer):
    """视频更新响应"""
    id = serializers.CharField(help_text="视频分析ID")
    status = serializers.CharField(help_text="状态")
    analysis_result = VideoAnalysisResultSerializer(help_text="分析结果")
    resume_id = serializers.CharField(required=False, help_text="关联简历ID")


# =============================================================================
# 最终推荐相关 Schema
# =============================================================================

class RecommendStatsSerializer(serializers.Serializer):
    """推荐统计"""
    analyzed_count = serializers.IntegerField(help_text="已分析人数")


class RecommendationSerializer(serializers.Serializer):
    """推荐结果"""
    level = serializers.CharField(help_text="推荐等级")
    label = serializers.CharField(help_text="推荐标签")
    action = serializers.CharField(help_text="建议行动")
    score = serializers.FloatField(help_text="推荐分数")


class ComprehensiveAnalysisSerializer(serializers.Serializer):
    """综合分析结果"""
    id = serializers.CharField(help_text="分析ID")
    resume_id = serializers.CharField(help_text="简历ID")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    final_score = serializers.FloatField(help_text="最终得分")
    recommendation = RecommendationSerializer(help_text="推荐结果")
    dimension_scores = serializers.DictField(
        child=DimensionScoreDetailSerializer(),
        help_text="维度评分（按维度名称索引）"
    )
    comprehensive_report = serializers.CharField(help_text="综合报告")
    created_at = serializers.DateTimeField(help_text="创建时间")


# =============================================================================
# 简历库相关 Schema
# =============================================================================

class LibraryItemSerializer(serializers.Serializer):
    """简历库列表项"""
    id = serializers.CharField(help_text="简历ID")
    filename = serializers.CharField(help_text="文件名")
    file_hash = serializers.CharField(help_text="文件哈希（前8位）")
    file_size = serializers.IntegerField(help_text="文件大小")
    file_type = serializers.CharField(help_text="文件类型")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    is_screened = serializers.BooleanField(help_text="是否已筛选")
    is_assigned = serializers.BooleanField(help_text="是否已分配")
    notes = serializers.CharField(allow_blank=True, help_text="备注")
    created_at = serializers.DateTimeField(help_text="创建时间")
    content_preview = serializers.CharField(help_text="内容预览")


class LibraryDetailSerializer(serializers.Serializer):
    """简历库详情"""
    id = serializers.CharField(help_text="简历ID")
    filename = serializers.CharField(help_text="文件名")
    file_hash = serializers.CharField(help_text="文件哈希")
    file_size = serializers.IntegerField(help_text="文件大小")
    file_type = serializers.CharField(help_text="文件类型")
    content = serializers.CharField(help_text="简历内容")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    is_screened = serializers.BooleanField(help_text="是否已筛选")
    is_assigned = serializers.BooleanField(help_text="是否已分配")
    notes = serializers.CharField(allow_blank=True, help_text="备注")
    created_at = serializers.DateTimeField(help_text="创建时间")
    updated_at = serializers.DateTimeField(help_text="更新时间")


class LibraryUploadItemSerializer(serializers.Serializer):
    """上传成功的简历项"""
    id = serializers.CharField(help_text="简历ID")
    filename = serializers.CharField(help_text="文件名")
    candidate_name = serializers.CharField(help_text="候选人姓名")


class LibrarySkippedItemSerializer(serializers.Serializer):
    """跳过的简历项"""
    filename = serializers.CharField(help_text="文件名")
    reason = serializers.CharField(help_text="跳过原因")


class LibraryUploadResponseSerializer(serializers.Serializer):
    """简历上传响应"""
    uploaded = LibraryUploadItemSerializer(many=True, help_text="上传成功列表")
    skipped = LibrarySkippedItemSerializer(many=True, help_text="跳过列表")
    uploaded_count = serializers.IntegerField(help_text="上传成功数量")
    skipped_count = serializers.IntegerField(help_text="跳过数量")


class HashCheckResponseSerializer(serializers.Serializer):
    """哈希检查响应"""
    exists = serializers.DictField(child=serializers.BooleanField(), help_text="哈希存在映射")
    existing_count = serializers.IntegerField(help_text="已存在数量")


# =============================================================================
# 岗位设置相关 Schema
# =============================================================================

class PositionItemSerializer(serializers.Serializer):
    """岗位项"""
    id = serializers.CharField(help_text="岗位ID")
    position = serializers.CharField(help_text="岗位名称")
    department = serializers.CharField(allow_blank=True, help_text="部门")
    description = serializers.CharField(allow_blank=True, help_text="岗位描述")
    required_skills = serializers.ListField(child=serializers.CharField(), help_text="必需技能")
    optional_skills = serializers.ListField(child=serializers.CharField(), help_text="可选技能")
    min_experience = serializers.IntegerField(help_text="最低经验年限")
    education = serializers.ListField(child=serializers.CharField(), help_text="学历要求")
    certifications = serializers.ListField(child=serializers.CharField(), help_text="证书要求")
    salary_range = serializers.ListField(child=serializers.IntegerField(), help_text="薪资范围")
    project_requirements = ProjectRequirementsSerializer(required=False, allow_null=True, help_text="项目要求")
    resume_count = serializers.IntegerField(help_text="简历数量")
    created_at = serializers.DateTimeField(help_text="创建时间")


class PositionResumeSerializer(serializers.Serializer):
    """岗位关联的简历"""
    id = serializers.CharField(help_text="简历ID")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    position_title = serializers.CharField(help_text="应聘岗位")
    resume_content = serializers.CharField(help_text="简历内容")
    screening_score = ScreeningScoreSerializer(allow_null=True, required=False, help_text="筛选得分")
    screening_summary = serializers.CharField(allow_null=True, help_text="筛选摘要")
    report_md_url = serializers.CharField(allow_null=True, help_text="MD报告URL")
    report_json_url = serializers.CharField(allow_null=True, help_text="JSON报告URL")
    created_at = serializers.DateTimeField(help_text="创建时间")


class PositionDetailSerializer(PositionItemSerializer):
    """岗位详情（含简历）"""
    resumes = PositionResumeSerializer(many=True, required=False, help_text="关联简历")


class PositionListDataSerializer(serializers.Serializer):
    """岗位列表数据"""
    positions = PositionItemSerializer(many=True, help_text="岗位列表")
    total = serializers.IntegerField(help_text="总数")


class AssignResumesResponseSerializer(serializers.Serializer):
    """分配简历响应"""
    position_id = serializers.CharField(help_text="岗位ID")
    assigned_count = serializers.IntegerField(help_text="分配数量")
    skipped_count = serializers.IntegerField(help_text="跳过数量")
    total_resumes = serializers.IntegerField(help_text="总简历数")


class RemoveResumeResponseSerializer(serializers.Serializer):
    """移除简历响应"""
    position_id = serializers.CharField(help_text="岗位ID")
    resume_id = serializers.CharField(help_text="简历ID")
    total_resumes = serializers.IntegerField(help_text="剩余简历数")


# =============================================================================
# 面试辅助相关 Schema
# =============================================================================

class SessionItemSerializer(serializers.Serializer):
    """会话列表项"""
    id = serializers.CharField(help_text="会话ID")
    resume_id = serializers.CharField(help_text="简历ID")
    qa_records = QARecordSerializer(many=True, help_text="问答记录")
    created_at = serializers.DateTimeField(help_text="创建时间")
    final_report = FinalReportSerializer(required=False, allow_null=True, help_text="最终报告")


class SessionCreateResponseSerializer(serializers.Serializer):
    """创建会话响应"""
    session_id = serializers.CharField(help_text="会话ID")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    position_title = serializers.CharField(help_text="应聘岗位")
    created_at = serializers.DateTimeField(help_text="创建时间")
    resume_summary = ResumeSummarySerializer(help_text="简历摘要")


class SessionDetailSerializer(serializers.Serializer):
    """会话详情"""
    session_id = serializers.CharField(help_text="会话ID")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    position_title = serializers.CharField(help_text="应聘岗位")
    current_round = serializers.IntegerField(help_text="当前轮次")
    qa_count = serializers.IntegerField(help_text="问答数量")
    is_completed = serializers.BooleanField(help_text="是否完成")
    created_at = serializers.DateTimeField(help_text="创建时间")
    updated_at = serializers.DateTimeField(help_text="更新时间")
    has_final_report = serializers.BooleanField(required=False, help_text="是否有最终报告")
    final_report_summary = serializers.CharField(required=False, help_text="报告摘要")


class InterestPointSerializer(serializers.Serializer):
    """兴趣点"""
    content = serializers.CharField(help_text="内容")
    question = serializers.CharField(help_text="相关问题")


class GenerateQuestionsResponseSerializer(serializers.Serializer):
    """生成问题响应"""
    session_id = serializers.CharField(help_text="会话ID")
    question_pool = InterviewQuestionSerializer(many=True, help_text="问题池")
    resume_highlights = serializers.ListField(child=serializers.CharField(), help_text="简历亮点")
    interest_points = InterestPointSerializer(many=True, help_text="兴趣点")


class CandidateQuestionSerializer(serializers.Serializer):
    """候选问题"""
    type = serializers.CharField(help_text="问题类型")
    content = serializers.CharField(help_text="问题内容")
    reason = serializers.CharField(required=False, help_text="推荐理由")


class RecordQAResponseSerializer(serializers.Serializer):
    """记录问答响应"""
    round_number = serializers.IntegerField(help_text="轮次")
    evaluation = AnswerEvaluationSerializer(allow_null=True, required=False, help_text="评估结果")
    candidate_questions = CandidateQuestionSerializer(many=True, help_text="候选问题")
    hr_action_hints = serializers.ListField(child=serializers.CharField(), help_text="HR行动提示")


class InterviewReportResponseSerializer(serializers.Serializer):
    """生成面试报告响应"""
    report = InterviewReportSerializer(help_text="报告内容")
    report_file_url = serializers.CharField(allow_null=True, help_text="报告文件URL")


# =============================================================================
# 简历筛选相关 Schema
# =============================================================================

class VideoAnalysisBriefSerializer(serializers.Serializer):
    """视频分析简要信息"""
    id = serializers.CharField(help_text="视频分析ID")
    video_name = serializers.CharField(help_text="视频名称")
    status = serializers.CharField(help_text="状态")
    confidence_score = serializers.FloatField(allow_null=True, help_text="置信度分数")


class ResumeDataItemSerializer(serializers.Serializer):
    """简历数据项"""
    id = serializers.CharField(help_text="简历数据ID")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    position_title = serializers.CharField(help_text="应聘岗位")
    screening_score = ScreeningScoreSerializer(allow_null=True, required=False, help_text="筛选得分")
    screening_summary = serializers.CharField(allow_null=True, help_text="筛选摘要")
    json_content = serializers.JSONField(allow_null=True, help_text="JSON内容（原始报告数据）")
    resume_content = serializers.CharField(help_text="简历内容")
    report_md_url = serializers.CharField(allow_null=True, help_text="MD报告URL")
    report_json_url = serializers.CharField(allow_null=True, help_text="JSON报告URL")
    video_analysis = VideoAnalysisBriefSerializer(required=False, help_text="视频分析")


class ResumeDataDetailSerializer(serializers.Serializer):
    """简历数据详情"""
    id = serializers.CharField(help_text="简历数据ID")
    created_at = serializers.DateTimeField(help_text="创建时间")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    position_title = serializers.CharField(help_text="应聘岗位")
    screening_score = ScreeningScoreSerializer(allow_null=True, required=False, help_text="筛选得分")
    screening_summary = serializers.CharField(allow_null=True, help_text="筛选摘要")
    resume_content = serializers.CharField(help_text="简历内容")
    json_report_content = serializers.JSONField(allow_null=True, help_text="JSON报告内容（原始报告数据）")
    report_json_url = serializers.CharField(allow_null=True, help_text="JSON报告URL")
    video_analysis_id = serializers.CharField(allow_null=True, help_text="视频分析ID")


class ResumeDataListSerializer(serializers.Serializer):
    """简历数据列表项（分页用）"""
    id = serializers.CharField(help_text="简历数据ID")
    created_at = serializers.DateTimeField(help_text="创建时间")
    position_title = serializers.CharField(help_text="应聘岗位")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    screening_score = ScreeningScoreSerializer(allow_null=True, required=False, help_text="筛选得分")
    resume_file_hash = serializers.CharField(help_text="文件哈希")
    report_md_url = serializers.CharField(allow_null=True, help_text="MD报告URL")
    report_json_url = serializers.CharField(allow_null=True, help_text="JSON报告URL")
    video_analysis = VideoAnalysisBriefSerializer(required=False, help_text="视频分析信息")


class ReportItemSerializer(serializers.Serializer):
    """报告项"""
    report_id = serializers.CharField(help_text="报告ID")
    report_filename = serializers.CharField(help_text="报告文件名")
    download_url = serializers.CharField(help_text="下载URL")
    resume_content = serializers.CharField(help_text="简历内容")


class TaskItemSerializer(serializers.Serializer):
    """任务项"""
    task_id = serializers.CharField(help_text="任务ID")
    status = serializers.ChoiceField(
        choices=['pending', 'running', 'completed', 'failed'],
        help_text="状态"
    )
    progress = serializers.IntegerField(help_text="进度")
    current_step = serializers.IntegerField(help_text="当前步骤")
    total_steps = serializers.IntegerField(help_text="总步骤")
    created_at = serializers.DateTimeField(help_text="创建时间")
    current_speaker = serializers.CharField(required=False, help_text="当前发言者")
    resume_data = ResumeDataItemSerializer(many=True, required=False, help_text="简历数据")
    reports = ReportItemSerializer(many=True, required=False, help_text="报告列表")
    error_message = serializers.CharField(required=False, help_text="错误信息")


class TaskStatusSerializer(serializers.Serializer):
    """任务状态响应"""
    task_id = serializers.CharField(help_text="任务ID")
    status = serializers.CharField(help_text="状态")
    progress = serializers.IntegerField(help_text="进度")
    current_step = serializers.IntegerField(help_text="当前步骤")
    total_steps = serializers.IntegerField(help_text="总步骤")
    created_at = serializers.DateTimeField(help_text="创建时间")
    current_speaker = serializers.CharField(required=False, help_text="当前发言者")
    resume_data = ResumeDataItemSerializer(many=True, required=False, help_text="简历数据")
    reports = ReportItemSerializer(many=True, required=False, help_text="报告列表")
    error_message = serializers.CharField(required=False, help_text="错误信息")


class TaskListDataSerializer(serializers.Serializer):
    """任务列表数据"""
    tasks = TaskItemSerializer(many=True, help_text="任务列表")
    total = serializers.IntegerField(help_text="总数")
    page = serializers.IntegerField(help_text="当前页")
    page_size = serializers.IntegerField(help_text="每页数量")


class LinkVideoResponseSerializer(serializers.Serializer):
    """关联视频响应"""
    resume_id = serializers.CharField(help_text="简历ID")
    video_analysis_id = serializers.CharField(help_text="视频分析ID")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    video_name = serializers.CharField(help_text="视频名称")


class UnlinkVideoResponseSerializer(serializers.Serializer):
    """解除关联响应"""
    resume_id = serializers.CharField(help_text="简历ID")
    disconnected_video_id = serializers.CharField(help_text="断开的视频ID")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    video_name = serializers.CharField(help_text="视频名称")


class GenerateResumesResponseSerializer(serializers.Serializer):
    """生成简历响应"""
    added = LibraryUploadItemSerializer(many=True, help_text="添加的简历")
    skipped = LibrarySkippedItemSerializer(many=True, help_text="跳过的简历")
    added_count = serializers.IntegerField(help_text="添加数量")
    skipped_count = serializers.IntegerField(help_text="跳过数量")
    requested_count = serializers.IntegerField(help_text="请求数量")


# =============================================================================
# 请求体 Schema
# =============================================================================

class PositionCreateRequestSerializer(serializers.Serializer):
    """创建岗位请求"""
    position = serializers.CharField(help_text="岗位名称")
    department = serializers.CharField(required=False, help_text="部门")
    description = serializers.CharField(required=False, help_text="岗位描述")
    required_skills = serializers.ListField(child=serializers.CharField(), required=False, help_text="必需技能")
    optional_skills = serializers.ListField(child=serializers.CharField(), required=False, help_text="可选技能")
    min_experience = serializers.IntegerField(required=False, help_text="最低经验年限")
    education = serializers.ListField(child=serializers.CharField(), required=False, help_text="学历要求")
    certifications = serializers.ListField(child=serializers.CharField(), required=False, help_text="证书要求")
    salary_range = serializers.ListField(child=serializers.IntegerField(), required=False, help_text="薪资范围")
    project_requirements = ProjectRequirementsSerializer(required=False, allow_null=True, help_text="项目要求")


class AssignResumesRequestSerializer(serializers.Serializer):
    """分配简历请求"""
    resume_ids = serializers.ListField(child=serializers.CharField(), help_text="简历ID列表")
    notes = serializers.CharField(required=False, help_text="备注")


class AIGenerateRequestSerializer(serializers.Serializer):
    """AI生成岗位请求"""
    description = serializers.CharField(help_text="岗位描述")
    documents = DocumentItemSerializer(many=True, required=False, help_text="参考文档")


class ResumeUploadItemSerializer(serializers.Serializer):
    """简历上传项"""
    name = serializers.CharField(help_text="文件名")
    content = serializers.CharField(help_text="简历内容")
    metadata = serializers.DictField(required=False, help_text="元数据（size, type等）")


class LibraryUploadRequestSerializer(serializers.Serializer):
    """简历上传请求"""
    resumes = ResumeUploadItemSerializer(many=True, help_text="简历列表")


class BatchDeleteRequestSerializer(serializers.Serializer):
    """批量删除请求"""
    resume_ids = serializers.ListField(child=serializers.CharField(), help_text="简历ID列表")


class HashCheckRequestSerializer(serializers.Serializer):
    """哈希检查请求"""
    hashes = serializers.ListField(child=serializers.CharField(), help_text="哈希值列表")


class SessionCreateRequestSerializer(serializers.Serializer):
    """创建会话请求"""
    resume_id = serializers.CharField(help_text="简历ID")
    job_config = serializers.JSONField(required=False, help_text="岗位配置")


class GenerateQuestionsRequestSerializer(serializers.Serializer):
    """生成问题请求"""
    categories = serializers.ListField(child=serializers.CharField(), required=False, help_text="问题类别")
    candidate_level = serializers.CharField(required=False, help_text="候选人级别")
    count_per_category = serializers.IntegerField(required=False, help_text="每类问题数量")
    focus_on_resume = serializers.BooleanField(required=False, help_text="是否聚焦简历")
    interest_point_count = serializers.IntegerField(required=False, help_text="兴趣点数量")


class RecordQARequestSerializer(serializers.Serializer):
    """记录问答请求"""
    question = QuestionInputSerializer(help_text="问题数据")
    answer = AnswerInputSerializer(help_text="回答数据")
    skip_evaluation = serializers.BooleanField(required=False, help_text="跳过评估")
    followup_count = serializers.IntegerField(required=False, help_text="追问数量")
    alternative_count = serializers.IntegerField(required=False, help_text="候选问题数量")


class GenerateReportRequestSerializer(serializers.Serializer):
    """生成报告请求"""
    include_conversation_log = serializers.BooleanField(required=False, help_text="包含对话记录")
    hr_notes = serializers.CharField(required=False, help_text="HR备注")


class LinkVideoRequestSerializer(serializers.Serializer):
    """关联视频请求"""
    resume_id = serializers.CharField(help_text="简历ID")
    video_analysis_id = serializers.CharField(help_text="视频分析ID")


class UnlinkVideoRequestSerializer(serializers.Serializer):
    """解除关联请求"""
    resume_id = serializers.CharField(help_text="简历ID")


class GenerateResumesPositionSerializer(serializers.Serializer):
    """生成简历用岗位信息"""
    position = serializers.CharField(help_text="岗位名称")
    description = serializers.CharField(required=False, help_text="岗位描述")
    required_skills = serializers.ListField(child=serializers.CharField(), required=False, help_text="必需技能")
    optional_skills = serializers.ListField(child=serializers.CharField(), required=False, help_text="可选技能")
    min_experience = serializers.IntegerField(required=False, help_text="最低经验年限")
    education = serializers.ListField(child=serializers.CharField(), required=False, help_text="学历要求")


class GenerateResumesRequestSerializer(serializers.Serializer):
    """生成简历请求"""
    position = GenerateResumesPositionSerializer(help_text="岗位信息")
    count = serializers.IntegerField(required=False, help_text="生成数量")


class ResumeDataCreateRequestSerializer(serializers.Serializer):
    """创建简历数据请求"""
    position_title = serializers.CharField(help_text="岗位名称")
    position_details = serializers.JSONField(required=False, help_text="岗位详情")
    candidate_name = serializers.CharField(help_text="候选人姓名")
    resume_content = serializers.CharField(help_text="简历内容")
