"""
最终推荐API视图模块 - 单人综合分析。

注意: 批量评估功能（InterviewEvaluationView）已废弃并移除。
"""
import logging

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.exceptions import ValidationException

from .models import CandidateComprehensiveAnalysis

logger = logging.getLogger(__name__)


# ============================================================================
# 已废弃的批量评估API（InterviewEvaluationView 和 ReportDownloadView）已移除
# 批量评估功能不再支持，请使用下方的 CandidateComprehensiveAnalysisView 进行单人分析
# ============================================================================


class CandidateComprehensiveAnalysisView(SafeAPIView):
    """
    单人综合分析API
    POST: 对单个候选人进行综合分析
    GET: 获取候选人的分析历史
    """
    
    def handle_get(self, request, resume_id=None):
        """获取候选人的分析历史。"""
        if not resume_id:
            raise ValidationException("缺少简历ID")
        
        # 获取最新的分析结果
        analysis = CandidateComprehensiveAnalysis.objects.filter(
            resume_data_id=resume_id
        ).order_by('-created_at').first()
        
        if not analysis:
            return ApiResponse.success(data=None)
        
        return ApiResponse.success(data={
            'id': str(analysis.id),
            'resume_id': str(analysis.resume_data_id),
            'candidate_name': analysis.resume_data.candidate_name,
            'final_score': analysis.final_score,
            'recommendation': {
                'level': analysis.recommendation_level,
                'label': analysis.recommendation_label,
                'action': analysis.recommendation_action,
                'score': analysis.final_score
            },
            'dimension_scores': analysis.dimension_scores,
            'comprehensive_report': analysis.comprehensive_report,
            'created_at': analysis.created_at.isoformat()
        })
    
    def handle_post(self, request, resume_id):
        """执行单人综合分析。"""
        from apps.resume_screening.models import ResumeData
        from apps.interview_assist.models import InterviewAssistSession
        from services.agents import CandidateComprehensiveAnalyzer
        
        # 获取简历数据
        resume = self.get_object_or_404(ResumeData, id=resume_id)
        
        # 获取简历内容
        resume_content = resume.resume_content or ""
        
        # 获取初筛报告
        screening_report = {
            "comprehensive_score": resume.screening_score.get("comprehensive_score") if resume.screening_score else None,
            "screening_summary": resume.screening_summary or ""
        }
        
        # 获取面试会话和报告
        interview_session = InterviewAssistSession.objects.filter(
            resume_data=resume
        ).order_by('-created_at').first()
        
        interview_records = []
        interview_report = {}
        
        if interview_session:
            interview_records = interview_session.qa_records or []
            interview_report = interview_session.final_report or {}
        
        # 检查是否有足够的数据
        if not screening_report.get("comprehensive_score") and not interview_report:
            raise ValidationException("缺少必要的分析数据（初筛报告或面试报告）")
        
        # 获取岗位配置
        job_config = {
            "title": resume.position_title or "未指定岗位"
        }
        if interview_session:
            job_config.update(interview_session.job_config or {})
        
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
            
            # 保存到数据库
            analysis = CandidateComprehensiveAnalysis.objects.create(
                resume_data=resume,
                final_score=result['final_score'],
                recommendation_level=result['recommendation']['level'],
                recommendation_label=result['recommendation']['label'],
                recommendation_action=result['recommendation']['action'],
                dimension_scores=result['dimension_scores'],
                comprehensive_report=result['comprehensive_report'],
                input_data_snapshot={
                    'screening_score': screening_report.get('comprehensive_score'),
                    'interview_qa_count': len(interview_records),
                    'has_interview_report': bool(interview_report),
                    'job_title': job_config.get('title')
                }
            )
            
            return ApiResponse.success(
                data={
                    'id': str(analysis.id),
                    'resume_id': str(resume.id),
                    'candidate_name': resume.candidate_name,
                    'final_score': result['final_score'],
                    'recommendation': result['recommendation'],
                    'dimension_scores': result['dimension_scores'],
                    'comprehensive_report': result['comprehensive_report'],
                    'created_at': analysis.created_at.isoformat()
                },
                message='综合分析完成'
            )
            
        except Exception as e:
            logger.error(f"综合分析失败: {e}", exc_info=True)
            raise ValidationException(f"综合分析失败: {str(e)}")
