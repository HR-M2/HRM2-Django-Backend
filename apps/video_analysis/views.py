"""
视频分析API视图模块 - 与原版 RecruitmentSystemAPI 返回格式保持一致。

数据库简化重构：
- VideoAnalysis 关联到 Resume（原关联 ResumeData）
- candidate_name/position_applied 从 Resume 关联获取
- 评分字段合并到 analysis_result JSON
"""
import logging

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.pagination import paginate_queryset
from apps.common.exceptions import ValidationException, NotFoundException
from apps.common.schemas import (
    api_response, success_response,
    VideoAnalysisItemSerializer, VideoAnalysisDetailSerializer,
    VideoUploadResponseSerializer, VideoUpdateResponseSerializer,
)

from .models import VideoAnalysis
from .services import VideoAnalysisService
from apps.resume.models import Resume

logger = logging.getLogger(__name__)


class VideoAnalysisView(SafeAPIView):
    """
    视频分析API
    POST: 上传视频并开始分析
    """
    
    @extend_schema(
        summary="上传视频并开始分析",
        description="上传视频文件并在后台开始分析",
        request={
            'multipart/form-data': inline_serializer(
                name='VideoUploadRequest',
                fields={
                    'video_file': serializers.FileField(help_text="视频文件"),
                    'candidate_name': serializers.CharField(help_text="候选人姓名"),
                    'position_applied': serializers.CharField(help_text="应聘岗位"),
                    'resume_id': serializers.CharField(required=False, help_text="关联简历ID"),
                    'video_name': serializers.CharField(required=False, help_text="视频名称"),
                }
            )
        },
        responses={201: api_response(VideoUploadResponseSerializer(), "VideoUpload")},
        tags=["videos"],
    )
    def handle_post(self, request):
        """上传视频并开始分析。"""
        video_file = request.FILES.get('video_file')
        candidate_name = self.get_param(request, 'candidate_name')
        position_applied = self.get_param(request, 'position_applied')
        resume_id = self.get_param(request, 'resume_id')
        video_name = self.get_param(request, 'video_name') or (video_file.name if video_file else None)
        
        if not video_file:
            raise ValidationException("缺少参数: video_file")
        
        if not video_name:
            raise ValidationException("无法确定视频名称")
        
        # 获取关联简历（新模型必须关联 Resume）
        resume = None
        if resume_id:
            try:
                resume = Resume.objects.get(id=resume_id)
                # 从 Resume 获取候选人信息
                if not candidate_name:
                    candidate_name = resume.candidate_name
                if not position_applied and resume.position:
                    position_applied = resume.position.title
            except Resume.DoesNotExist:
                raise NotFoundException("指定的简历不存在")
        
        if not resume:
            raise ValidationException("必须提供 resume_id 关联简历")
        
        # 创建视频分析记录（关联到 Resume）
        video_analysis = VideoAnalysis.objects.create(
            resume=resume,
            video_name=video_name,
            video_file=video_file,
            status='pending'
        )
        
        # 开始分析
        self._start_analysis(video_analysis)
        
        response_data = {
            "id": str(video_analysis.id),
            "video_name": video_analysis.video_name,
            "candidate_name": resume.candidate_name,
            "position_applied": resume.position.title if resume.position else None,
            "resume_id": str(resume.id),
            "status": video_analysis.status,
            "created_at": video_analysis.created_at.isoformat()
        }
        
        # 返回统一格式
        return ApiResponse.created(
            data=response_data,
            message="视频数据接收成功，分析已在后台开始"
        )
    
    def _start_analysis(self, video_analysis):
        """在后台启动视频分析（使用线程）。"""
        import threading
        import time
        
        def run_analysis():
            time.sleep(1)  # 短暂延迟确保响应先返回
            VideoAnalysisService.analyze_video(str(video_analysis.id))
        
        thread = threading.Thread(target=run_analysis)
        thread.daemon = True
        thread.start()
        logger.info(f"Started thread for video analysis {video_analysis.id}")


class VideoAnalysisStatusView(SafeAPIView):
    """
    视频分析状态API
    GET: 获取视频分析状态和结果
    """
    
    @extend_schema(
        summary="获取视频分析状态",
        description="获取指定视频的分析状态和结果",
        responses={200: api_response(VideoAnalysisDetailSerializer(), "VideoStatus")},
        tags=["videos"],
    )
    def handle_get(self, request, video_id):
        """获取视频分析状态。"""
        video_analysis = self.get_object_or_404(VideoAnalysis, id=video_id)
        
        # 从关联的 Resume 获取候选人信息
        resume = video_analysis.resume
        response_data = {
            "id": str(video_analysis.id),
            "video_name": video_analysis.video_name,
            "candidate_name": resume.candidate_name if resume else None,
            "position_applied": resume.position.title if resume and resume.position else None,
            "resume_id": str(resume.id) if resume else None,
            "status": video_analysis.status,
            "created_at": video_analysis.created_at.isoformat()
        }
        
        if video_analysis.status == 'completed' and video_analysis.analysis_result:
            response_data.update({
                "analysis_result": video_analysis.analysis_result,
                "summary": video_analysis.analysis_result.get('summary'),
                "confidence_score": video_analysis.analysis_result.get('confidence_score')
            })
        
        if video_analysis.status == 'failed' and video_analysis.error_message:
            response_data["error_message"] = video_analysis.error_message
        
        # 返回与原版一致的格式
        return ApiResponse.success(data=response_data)


class VideoAnalysisUpdateView(SafeAPIView):
    """
    视频分析结果更新API
    POST: 更新视频分析结果
    """
    
    @extend_schema(
        summary="更新视频分析结果",
        description="更新视频分析的各项评分和状态",
        request=inline_serializer(
            name='VideoUpdateRequest',
            fields={
                'fraud_score': serializers.FloatField(required=False, help_text="欺诈评分"),
                'neuroticism_score': serializers.FloatField(required=False, help_text="神经质评分"),
                'extraversion_score': serializers.FloatField(required=False, help_text="外向性评分"),
                'openness_score': serializers.FloatField(required=False, help_text="开放性评分"),
                'agreeableness_score': serializers.FloatField(required=False, help_text="宜人性评分"),
                'conscientiousness_score': serializers.FloatField(required=False, help_text="尽责性评分"),
                'summary': serializers.CharField(required=False, help_text="分析摘要"),
                'confidence_score': serializers.FloatField(required=False, help_text="置信度"),
                'status': serializers.CharField(required=False, help_text="状态"),
            }
        ),
        responses={200: api_response(VideoUpdateResponseSerializer(), "VideoUpdate")},
        tags=["videos"],
    )
    def handle_post(self, request, video_id):
        """更新视频分析结果。"""
        scores = {
            'fraud_score': request.data.get('fraud_score'),
            'neuroticism_score': request.data.get('neuroticism_score'),
            'extraversion_score': request.data.get('extraversion_score'),
            'openness_score': request.data.get('openness_score'),
            'agreeableness_score': request.data.get('agreeableness_score'),
            'conscientiousness_score': request.data.get('conscientiousness_score'),
            'summary': request.data.get('summary'),
            'confidence_score': request.data.get('confidence_score'),
            'status': request.data.get('status', 'completed'),
        }
        
        # 将适用的字段转换为浮点数
        for key in ['fraud_score', 'neuroticism_score', 'extraversion_score',
                    'openness_score', 'agreeableness_score', 'conscientiousness_score',
                    'confidence_score']:
            if scores[key] is not None:
                try:
                    scores[key] = float(scores[key])
                except (TypeError, ValueError):
                    raise ValidationException(f"{key}必须是有效的数字")
        
        video_analysis = VideoAnalysisService.update_analysis_result(video_id, **scores)
        
        response_data = {
            "id": str(video_analysis.id),
            "status": video_analysis.status,
            "analysis_result": video_analysis.analysis_result
        }
        
        if video_analysis.resume:
            response_data["resume_id"] = str(video_analysis.resume.id)
        
        # 返回与原版一致的格式
        return ApiResponse.success(
            data=response_data,
            message="视频分析结果更新成功"
        )


class VideoAnalysisListView(SafeAPIView):
    """
    视频分析列表API
    GET: 获取视频分析列表
    """
    
    @extend_schema(
        summary="获取视频分析列表",
        description="获取视频分析列表，支持过滤和分页",
        parameters=[
            OpenApiParameter(name='candidate_name', type=str, description='候选人姓名过滤'),
            OpenApiParameter(name='position_applied', type=str, description='应聘岗位过滤'),
            OpenApiParameter(name='status', type=str, description='状态过滤'),
            OpenApiParameter(name='page', type=int, description='页码'),
            OpenApiParameter(name='page_size', type=int, description='每页数量'),
        ],
        responses={200: api_response(
            inline_serializer(
                name='VideoListData',
                fields={
                    'videos': VideoAnalysisItemSerializer(many=True),
                    'total': serializers.IntegerField(),
                    'page': serializers.IntegerField(),
                    'page_size': serializers.IntegerField(),
                }
            ),
            "VideoList"
        )},
        tags=["videos"],
    )
    def handle_get(self, request):
        """获取视频分析列表，支持过滤和分页。"""
        candidate_name = request.GET.get('candidate_name')
        position_applied = request.GET.get('position_applied')
        status_filter = request.GET.get('status')
        
        queryset = VideoAnalysis.objects.all().order_by('-created_at')
        
        if candidate_name:
            queryset = queryset.filter(candidate_name__icontains=candidate_name)
        if position_applied:
            queryset = queryset.filter(position_applied__icontains=position_applied)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        items, pagination = paginate_queryset(queryset, request)
        
        result = []
        for video in items:
            resume = video.resume
            data = {
                "id": str(video.id),
                "video_name": video.video_name,
                "candidate_name": resume.candidate_name if resume else None,
                "position_applied": resume.position.title if resume and resume.position else None,
                "resume_id": str(resume.id) if resume else None,
                "status": video.status,
                "confidence_score": video.analysis_result.get('confidence_score') if video.analysis_result else None,
                "created_at": video.created_at.isoformat()
            }
            
            if video.status == 'completed' and video.analysis_result:
                data["analysis_result"] = video.analysis_result
            
            result.append(data)
        
        # 返回与原版完全一致的格式
        return ApiResponse.success(data={
            "videos": result,
            "total": pagination['total'],
            "page": pagination['page'],
            "page_size": pagination['page_size']
        })
