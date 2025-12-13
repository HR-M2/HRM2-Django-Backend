"""
简历数据详情视图模块
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

from ..models import ResumeData

logger = logging.getLogger(__name__)


class ResumeDataDetailView(SafeAPIView):
    """
    简历数据详情API
    GET: 获取简历数据详情
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
        resume_data = self.get_object_or_404(ResumeData, id=resume_id)
        
        # 解析分数
        scores = {}
        if resume_data.screening_score:
            scores = {
                "hr_score": resume_data.screening_score.get("hr_score", 0),
                "technical_score": resume_data.screening_score.get("technical_score", 0),
                "manager_score": resume_data.screening_score.get("manager_score", 0),
                "comprehensive_score": resume_data.screening_score.get("comprehensive_score", 0)
            }
        
        data = {
            "id": str(resume_data.id),
            "created_at": resume_data.created_at.isoformat(),
            "candidate_name": resume_data.candidate_name,
            "position_title": resume_data.position_title,
            "screening_score": scores,
            "screening_summary": resume_data.screening_summary,
            "resume_content": resume_data.resume_content,
            "json_report_content": resume_data.json_report_content,
            "report_json_url": resume_data.report_json_file.url if resume_data.report_json_file else None,
            "video_analysis_id": str(resume_data.video_analysis.id) if resume_data.video_analysis else None,
        }
        
        # 返回与原版一致的格式
        return ApiResponse.success(data={"report": data})
