"""
最终推荐API视图模块 - 单人综合分析。

数据库简化重构：
- 使用 ComprehensiveAnalysis 模型（原 CandidateComprehensiveAnalysis 已重命名+简化）
- 关联到 Resume（原关联 ResumeData）
- recommendation 字段合并为 JSON
- InterviewEvaluationTask 已删除
"""
import logging

from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.exceptions import ValidationException
from apps.common.schemas import (
    api_response, success_response,
    RecommendStatsSerializer, ComprehensiveAnalysisSerializer,
)

from .models import ComprehensiveAnalysis
from apps.resume.models import Resume
from apps.interview_assist.models import InterviewSession

logger = logging.getLogger(__name__)


# ============================================================================
# 已废弃的批量评估API（InterviewEvaluationView 和 ReportDownloadView）已移除
# 批量评估功能不再支持，请使用下方的 CandidateComprehensiveAnalysisView 进行单人分析
# ============================================================================


class RecommendStatsView(SafeAPIView):
    """
    推荐统计API
    GET: 获取已完成综合分析的统计数据
    """
    
    @extend_schema(
        summary="获取推荐统计",
        description="获取已完成综合分析的统计数据",
        responses={200: api_response(RecommendStatsSerializer(), "RecommendStats")},
        tags=["recommend"],
    )
    def handle_get(self, request):
        """获取已总结推荐的数量统计。"""
        # 统计已完成综合分析的唯一简历数量（每个简历只算一次）
        analyzed_count = ComprehensiveAnalysis.objects.values(
            'resume_id'
        ).distinct().count()
        
        return ApiResponse.success(data={
            'analyzed_count': analyzed_count
        })


class ComprehensiveAnalysisView(SafeAPIView):
    """
    综合分析API
    POST: 对单个候选人进行综合分析
    GET: 获取候选人的分析历史
    """
    
    @extend_schema(
        summary="获取综合分析历史",
        description="获取候选人的综合分析历史记录",
        responses={
            200: api_response(ComprehensiveAnalysisSerializer(allow_null=True), "ComprehensiveAnalysisGet"),
        },
        tags=["recommend"],
    )
    def handle_get(self, request, resume_id=None):
        """获取候选人的分析历史。"""
        if not resume_id:
            raise ValidationException("缺少简历ID")
        
        # 获取最新的分析结果
        analysis = ComprehensiveAnalysis.objects.filter(
            resume_id=resume_id
        ).order_by('-created_at').first()
        
        if not analysis:
            return ApiResponse.success(data=None)
        
        # 从 Resume 获取候选人信息
        resume = analysis.resume
        
        return ApiResponse.success(data={
            'id': str(analysis.id),
            'resume_id': str(analysis.resume_id),
            'candidate_name': resume.candidate_name if resume else None,
            'final_score': analysis.final_score,
            'recommendation': analysis.recommendation,
            'dimension_scores': analysis.dimension_scores,
            'comprehensive_report': analysis.report,
            'created_at': analysis.created_at.isoformat()
        })
    
    @extend_schema(
        summary="执行综合分析",
        description="对单个候选人进行综合分析，整合初筛报告和面试报告",
        request=None,
        responses={
            200: api_response(ComprehensiveAnalysisSerializer(), "ComprehensiveAnalysisPost"),
        },
        tags=["recommend"],
    )
    def handle_post(self, request, resume_id):
        """执行单人综合分析。"""
        from services.agents import CandidateComprehensiveAnalyzer
        
        # 获取简历
        resume = self.get_object_or_404(Resume, id=resume_id)
        
        # 获取简历内容
        resume_content = resume.content or ""
        
        # 获取初筛报告（从 Resume.screening_result）
        screening_report = {
            "comprehensive_score": resume.screening_result.get("score") if resume.screening_result else None,
            "screening_summary": resume.screening_result.get("summary", "") if resume.screening_result else ""
        }
        
        # 获取面试会话和报告
        interview_session = InterviewSession.objects.filter(
            resume=resume
        ).order_by('-created_at').first()
        
        interview_records = []
        interview_report = {}
        
        if interview_session:
            interview_records = interview_session.qa_records or []
            interview_report = interview_session.final_report or {}
        
        # 检查是否有足够的数据
        if not screening_report.get("comprehensive_score") and not interview_report:
            raise ValidationException("缺少必要的分析数据（初筛报告或面试报告）")
        
        # 从 resume.position 获取岗位配置
        job_config = {
            "title": resume.position.title if resume.position else "未指定岗位"
        }
        if resume.position:
            job_config['requirements'] = resume.position.requirements or {}
        
        # 执行综合分析
        analyzer = CandidateComprehensiveAnalyzer(job_config=job_config)
        
        try:
            result = analyzer.analyze(
                candidate_name=resume.candidate_name,
                resume_content=resume_content,
                screening_report=screening_report,
                interview_records=interview_records,
                interview_report=interview_report,
                video_analysis=None  # 预留
            )
            
            # 保存到数据库（使用新的 ComprehensiveAnalysis 模型）
            analysis = ComprehensiveAnalysis.objects.create(
                resume=resume,
                final_score=result['final_score'],
                recommendation=result['recommendation'],
                dimension_scores=result['dimension_scores'],
                report=result.get('comprehensive_report', '')
            )
            
            # 更新简历状态为已分析
            resume.update_status(Resume.Status.ANALYZED)
            
            return ApiResponse.success(
                data={
                    'id': str(analysis.id),
                    'resume_id': str(resume.id),
                    'candidate_name': resume.candidate_name,
                    'final_score': result['final_score'],
                    'recommendation': result['recommendation'],
                    'dimension_scores': result['dimension_scores'],
                    'comprehensive_report': result.get('comprehensive_report', ''),
                    'created_at': analysis.created_at.isoformat()
                },
                message='综合分析完成'
            )
            
        except Exception as e:
            logger.error(f"综合分析失败: {e}", exc_info=True)
            raise ValidationException(f"综合分析失败: {str(e)}")
