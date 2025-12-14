"""
简历数据详情视图模块

数据库简化重构：
- 使用 Resume 模型（原 ResumeData 已合并到 Resume）
"""
import logging

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.schemas import (
    api_response,
    ResumeDataDetailSerializer,
)

from apps.resume.models import Resume

logger = logging.getLogger(__name__)


class ScreeningReportView(SafeAPIView):
    """
    筛选报告详情API
    GET: 获取筛选报告详情
    """
    
    @extend_schema(
        summary="获取简历数据详情",
        description="获取指定简历数据的详细信息",
        responses={200: api_response(
            inline_serializer(
                name='ResumeDataReportWrapper',
                fields={'report': ResumeDataDetailSerializer()}
            ),
            "ResumeDataDetail"
        )},
        tags=["screening"],
    )
    def handle_get(self, request, resume_id):
        """获取简历数据详情。"""
        resume = self.get_object_or_404(Resume, id=resume_id)
        
        # 解析分数（从 screening_result JSON）
        scores = {}
        if resume.screening_result:
            scores = {
                "hr_score": resume.screening_result.get("hr_score", 0),
                "technical_score": resume.screening_result.get("technical_score", 0),
                "manager_score": resume.screening_result.get("manager_score", 0),
                "comprehensive_score": resume.screening_result.get("score", 0)
            }
        
        data = {
            "id": str(resume.id),
            "created_at": resume.created_at.isoformat(),
            "candidate_name": resume.candidate_name,
            "position_title": resume.position.title if resume.position else None,
            "screening_score": scores,
            "screening_summary": resume.screening_result.get('summary') if resume.screening_result else None,
            "resume_content": resume.content,
            "screening_report": resume.screening_report,
            "video_analysis_id": str(resume.video_analyses.first().id) if resume.video_analyses.exists() else None,
        }
        
        # 返回与原版一致的格式
        return ApiResponse.success(data={"report": data})
