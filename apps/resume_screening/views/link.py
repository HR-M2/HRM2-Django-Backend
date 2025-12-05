"""
简历-视频关联视图模块 - 与原版 RecruitmentSystemAPI 返回格式保持一致。
"""
import logging
from rest_framework.response import Response
from rest_framework import status

from apps.common.mixins import SafeAPIView
from apps.common.response import APIResponse
from apps.common.exceptions import ValidationException, NotFoundException

from ..models import ResumeData

logger = logging.getLogger(__name__)


class LinkResumeVideoView(SafeAPIView):
    """
    关联简历与视频API
    POST: 建立简历与视频分析的关联
    """
    
    def handle_post(self, request):
        """将简历数据与视频分析关联。"""
        from apps.video_analysis.models import VideoAnalysis
        
        resume_data_id = self.get_param(request, 'resume_data_id', required=True)
        video_analysis_id = self.get_param(request, 'video_analysis_id', required=True)
        
        # 获取简历数据
        try:
            resume_data = ResumeData.objects.get(id=resume_data_id)
        except ResumeData.DoesNotExist:
            raise NotFoundException("简历数据不存在")
        
        # 获取视频分析
        try:
            video_analysis = VideoAnalysis.objects.get(id=video_analysis_id)
        except VideoAnalysis.DoesNotExist:
            raise NotFoundException("视频分析记录不存在")
        
        # 检查是否已关联
        if resume_data.video_analysis:
            raise ValidationException(
                "该简历数据已关联视频分析记录",
                {"existing_video_id": str(resume_data.video_analysis.id)}
            )
        
        # 创建关联
        resume_data.video_analysis = video_analysis
        resume_data.save()
        
        # 返回与原版一致的格式
        return Response({
            "message": "简历数据与视频分析记录关联成功",
            "resume_data_id": str(resume_data.id),
            "video_analysis_id": str(video_analysis.id),
            "candidate_name": resume_data.candidate_name,
            "video_name": video_analysis.video_name
        }, status=status.HTTP_200_OK)


class UnlinkResumeVideoView(SafeAPIView):
    """
    解除简历与视频关联API
    POST: 解除简历与视频分析的关联
    """
    
    def handle_post(self, request):
        """解除简历数据与视频分析的关联。"""
        resume_data_id = self.get_param(request, 'resume_data_id', required=True)
        
        # 获取简历数据
        try:
            resume_data = ResumeData.objects.get(id=resume_data_id)
        except ResumeData.DoesNotExist:
            raise NotFoundException("简历数据不存在")
        
        # 检查是否已关联
        if not resume_data.video_analysis:
            raise ValidationException("该简历数据未关联任何视频分析记录")
        
        # 在取消关联前获取视频信息
        video_analysis = resume_data.video_analysis
        video_name = video_analysis.video_name
        video_id = str(video_analysis.id)
        
        # 移除关联
        resume_data.video_analysis = None
        resume_data.save()
        
        # 返回与原版一致的格式
        return Response({
            "message": "简历数据与视频分析记录解除关联成功",
            "resume_data_id": str(resume_data.id),
            "disconnected_video_id": video_id,
            "candidate_name": resume_data.candidate_name,
            "video_name": video_name
        }, status=status.HTTP_200_OK)
