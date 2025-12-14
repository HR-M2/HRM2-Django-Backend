"""
简历管理API视图模块。

数据库简化重构：
- 合并原 LibraryView 和部分 ScreeningView 功能
- 实现: 列表、详情、上传、更新、删除、分配
"""
import logging

from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from rest_framework import serializers

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.pagination import paginate_queryset
from apps.common.exceptions import ValidationException, NotFoundException
from apps.common.utils import generate_hash

from .models import Resume
from .serializers import (
    ResumeListSerializer, ResumeDetailSerializer,
    ResumeCreateSerializer, ResumeUpdateSerializer,
    ResumeUploadSerializer, BatchDeleteSerializer,
    CheckHashSerializer, ResumeAssignSerializer,
)

logger = logging.getLogger(__name__)


class ResumeListView(SafeAPIView):
    """
    简历列表API
    GET: 获取简历列表（支持过滤和分页）
    POST: 批量上传简历
    """
    
    @extend_schema(
        summary="获取简历列表",
        description="获取简历列表，支持按岗位、状态、候选人过滤，支持分页",
        operation_id="resumes_list",
        parameters=[
            OpenApiParameter(name='position_id', type=str, description='岗位ID过滤'),
            OpenApiParameter(name='status', type=str, description='状态过滤'),
            OpenApiParameter(name='candidate_name', type=str, description='候选人姓名搜索'),
            OpenApiParameter(name='is_assigned', type=bool, description='是否已分配岗位'),
            OpenApiParameter(name='page', type=int, description='页码'),
            OpenApiParameter(name='page_size', type=int, description='每页数量'),
        ],
        responses={200: inline_serializer(
            name='ResumeListResponse',
            fields={
                'resumes': ResumeListSerializer(many=True),
                'total': serializers.IntegerField(),
                'page': serializers.IntegerField(),
                'page_size': serializers.IntegerField(),
            }
        )},
        tags=["resumes"],
    )
    def handle_get(self, request):
        """获取简历列表。"""
        position_id = request.GET.get('position_id')
        status_filter = request.GET.get('status')
        candidate_name = request.GET.get('candidate_name')
        is_assigned = request.GET.get('is_assigned')
        
        queryset = Resume.objects.all().order_by('-created_at')
        
        if position_id:
            queryset = queryset.filter(position_id=position_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if candidate_name:
            queryset = queryset.filter(candidate_name__icontains=candidate_name)
        if is_assigned is not None:
            if is_assigned in ['true', 'True', '1', True]:
                queryset = queryset.filter(position__isnull=False)
            elif is_assigned in ['false', 'False', '0', False]:
                queryset = queryset.filter(position__isnull=True)
        
        items, pagination = paginate_queryset(queryset, request)
        serializer = ResumeListSerializer(items, many=True)
        
        return ApiResponse.success(data={
            'resumes': serializer.data,
            'total': pagination['total'],
            'page': pagination['page'],
            'page_size': pagination['page_size'],
        })
    
    @extend_schema(
        summary="批量上传简历",
        description="批量上传简历文件内容",
        request=ResumeUploadSerializer,
        responses={201: inline_serializer(
            name='ResumeUploadResponse',
            fields={
                'created_count': serializers.IntegerField(),
                'skipped_count': serializers.IntegerField(),
                'resumes': ResumeListSerializer(many=True),
            }
        )},
        tags=["resumes"],
    )
    def handle_post(self, request):
        """批量上传简历。"""
        serializer = ResumeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        resumes_data = serializer.validated_data['resumes']
        created_resumes = []
        skipped_count = 0
        
        for item in resumes_data:
            name = item.get('name', '')
            content = item.get('content', '')
            metadata = item.get('metadata', {})
            
            if not content:
                skipped_count += 1
                continue
            
            file_hash = generate_hash(content)
            
            if Resume.objects.filter(file_hash=file_hash).exists():
                skipped_count += 1
                continue
            
            candidate_name = metadata.get('candidate_name', '')
            if not candidate_name:
                candidate_name = self._extract_candidate_name(content) or name.rsplit('.', 1)[0]
            
            resume = Resume.objects.create(
                filename=name,
                file_hash=file_hash,
                file_size=len(content.encode('utf-8')),
                file_type=metadata.get('file_type', name.rsplit('.', 1)[-1] if '.' in name else ''),
                candidate_name=candidate_name,
                content=content,
                notes=metadata.get('notes', ''),
            )
            created_resumes.append(resume)
        
        response_serializer = ResumeListSerializer(created_resumes, many=True)
        
        return ApiResponse.created(
            data={
                'created_count': len(created_resumes),
                'skipped_count': skipped_count,
                'resumes': response_serializer.data,
            },
            message=f'成功上传 {len(created_resumes)} 份简历，跳过 {skipped_count} 份重复简历'
        )
    
    def _extract_candidate_name(self, content: str) -> str:
        """从简历内容中提取候选人姓名。"""
        lines = content.strip().split('\n')[:10]
        for line in lines:
            line = line.strip()
            if line and len(line) <= 20:
                if any(keyword in line.lower() for keyword in ['姓名', 'name', '简历']):
                    parts = line.replace('：', ':').split(':')
                    if len(parts) > 1:
                        return parts[1].strip()
                elif not any(char in line for char in ['@', 'http', '/', '\\', '.com']):
                    return line
        return ''


class ResumeDetailView(SafeAPIView):
    """
    简历详情API
    GET: 获取简历详情
    PUT: 更新简历信息
    DELETE: 删除简历
    """
    
    @extend_schema(
        summary="获取简历详情",
        description="获取指定简历的详细信息",
        operation_id="resumes_detail",
        responses={200: ResumeDetailSerializer},
        tags=["resumes"],
    )
    def handle_get(self, request, resume_id):
        """获取简历详情。"""
        resume = self.get_object_or_404(Resume, id=resume_id)
        serializer = ResumeDetailSerializer(resume)
        return ApiResponse.success(data=serializer.data)
    
    @extend_schema(
        summary="更新简历信息",
        description="更新简历的候选人姓名、状态、岗位、备注等",
        request=ResumeUpdateSerializer,
        responses={200: ResumeDetailSerializer},
        tags=["resumes"],
    )
    def handle_put(self, request, resume_id):
        """更新简历信息。"""
        resume = self.get_object_or_404(Resume, id=resume_id)
        serializer = ResumeUpdateSerializer(resume, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        response_serializer = ResumeDetailSerializer(resume)
        return ApiResponse.success(data=response_serializer.data, message='简历更新成功')
    
    @extend_schema(
        summary="删除简历",
        description="删除指定简历",
        responses={200: inline_serializer(name='ResumeDeleteResponse', fields={})},
        tags=["resumes"],
    )
    def handle_delete(self, request, resume_id):
        """删除简历。"""
        resume = self.get_object_or_404(Resume, id=resume_id)
        resume.delete()
        return ApiResponse.success(message='简历已删除')


class ResumeBatchDeleteView(SafeAPIView):
    """
    批量删除简历API
    POST: 批量删除简历
    """
    
    @extend_schema(
        summary="批量删除简历",
        description="批量删除指定的简历",
        request=BatchDeleteSerializer,
        responses={200: inline_serializer(
            name='BatchDeleteResponse',
            fields={
                'deleted_count': serializers.IntegerField(),
            }
        )},
        tags=["resumes"],
    )
    def handle_post(self, request):
        """批量删除简历。"""
        serializer = BatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        resume_ids = serializer.validated_data['resume_ids']
        deleted_count = Resume.objects.filter(id__in=resume_ids).delete()[0]
        
        return ApiResponse.success(
            data={'deleted_count': deleted_count},
            message=f'成功删除 {deleted_count} 份简历'
        )


class ResumeCheckHashView(SafeAPIView):
    """
    检查简历哈希API
    POST: 检查哪些简历已存在
    """
    
    @extend_schema(
        summary="检查简历哈希",
        description="检查哪些简历哈希值已存在（用于上传前去重）",
        request=CheckHashSerializer,
        responses={200: inline_serializer(
            name='CheckHashResponse',
            fields={
                'existing_hashes': serializers.ListField(child=serializers.CharField()),
            }
        )},
        tags=["resumes"],
    )
    def handle_post(self, request):
        """检查简历哈希。"""
        serializer = CheckHashSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        hashes = serializer.validated_data['hashes']
        existing = Resume.objects.filter(file_hash__in=hashes).values_list('file_hash', flat=True)
        
        return ApiResponse.success(data={
            'existing_hashes': list(existing)
        })


class ResumeAssignView(SafeAPIView):
    """
    简历分配岗位API
    POST: 批量分配或取消分配简历到岗位
    """
    
    @extend_schema(
        summary="分配简历到岗位",
        description="批量将简历分配到指定岗位，或取消分配",
        request=ResumeAssignSerializer,
        responses={200: inline_serializer(
            name='ResumeAssignResponse',
            fields={
                'updated_count': serializers.IntegerField(),
                'position_id': serializers.CharField(allow_null=True),
            }
        )},
        tags=["resumes"],
    )
    def handle_post(self, request):
        """分配简历到岗位。"""
        from apps.position_settings.models import Position
        
        serializer = ResumeAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        resume_ids = serializer.validated_data['resume_ids']
        position_id = serializer.validated_data.get('position_id')
        
        position = None
        if position_id:
            try:
                position = Position.objects.get(id=position_id, is_active=True)
            except Position.DoesNotExist:
                raise NotFoundException(f"岗位不存在: {position_id}")
        
        updated_count = Resume.objects.filter(id__in=resume_ids).update(position=position)
        
        action = f"分配到岗位 {position.title}" if position else "取消分配"
        return ApiResponse.success(
            data={
                'updated_count': updated_count,
                'position_id': str(position_id) if position_id else None,
            },
            message=f'成功{action} {updated_count} 份简历'
        )


class ResumeScreeningResultView(SafeAPIView):
    """
    简历筛选结果API
    GET: 获取简历筛选结果
    PUT: 更新简历筛选结果
    """
    
    @extend_schema(
        summary="获取筛选结果",
        description="获取简历的筛选结果和报告",
        responses={200: inline_serializer(
            name='ScreeningResultResponse',
            fields={
                'resume_id': serializers.CharField(),
                'status': serializers.CharField(),
                'screening_result': serializers.JSONField(allow_null=True),
                'screening_report': serializers.CharField(allow_null=True),
            }
        )},
        tags=["resumes"],
    )
    def handle_get(self, request, resume_id):
        """获取筛选结果。"""
        resume = self.get_object_or_404(Resume, id=resume_id)
        
        return ApiResponse.success(data={
            'resume_id': str(resume.id),
            'candidate_name': resume.candidate_name,
            'status': resume.status,
            'screening_result': resume.screening_result,
            'screening_report': resume.screening_report,
        })
    
    @extend_schema(
        summary="更新筛选结果",
        description="更新简历的筛选结果（通常由筛选任务调用）",
        request=inline_serializer(
            name='UpdateScreeningResultRequest',
            fields={
                'screening_result': serializers.JSONField(),
                'screening_report': serializers.CharField(required=False),
            }
        ),
        responses={200: inline_serializer(
            name='UpdateScreeningResultResponse',
            fields={
                'resume_id': serializers.CharField(),
                'status': serializers.CharField(),
            }
        )},
        tags=["resumes"],
    )
    def handle_put(self, request, resume_id):
        """更新筛选结果。"""
        resume = self.get_object_or_404(Resume, id=resume_id)
        
        screening_result = request.data.get('screening_result')
        screening_report = request.data.get('screening_report')
        
        if screening_result is None:
            raise ValidationException("缺少筛选结果")
        
        resume.set_screening_result(screening_result, screening_report)
        
        return ApiResponse.success(
            data={
                'resume_id': str(resume.id),
                'status': resume.status,
            },
            message='筛选结果已更新'
        )


class ResumeStatsView(SafeAPIView):
    """
    简历统计API
    GET: 获取简历统计数据
    """
    
    @extend_schema(
        summary="获取简历统计",
        description="获取简历的各项统计数据",
        responses={200: inline_serializer(
            name='ResumeStatsResponse',
            fields={
                'total_count': serializers.IntegerField(),
                'pending_count': serializers.IntegerField(),
                'screened_count': serializers.IntegerField(),
                'interviewing_count': serializers.IntegerField(),
                'analyzed_count': serializers.IntegerField(),
                'assigned_count': serializers.IntegerField(),
                'unassigned_count': serializers.IntegerField(),
            }
        )},
        tags=["resumes"],
    )
    def handle_get(self, request):
        """获取简历统计。"""
        from django.db.models import Count, Q
        from apps.interview_assist.models import InterviewSession
        
        stats = Resume.objects.aggregate(
            total_count=Count('id'),
            pending_count=Count('id', filter=Q(status=Resume.Status.PENDING)),
            screened_count=Count('id', filter=Q(status=Resume.Status.SCREENED)),
            interviewing_count=Count('id', filter=Q(status=Resume.Status.INTERVIEWING)),
            analyzed_count=Count('id', filter=Q(status=Resume.Status.ANALYZED)),
            assigned_count=Count('id', filter=Q(position__isnull=False)),
            unassigned_count=Count('id', filter=Q(position__isnull=True)),
        )
        
        # 添加面试统计
        stats['interview_total'] = InterviewSession.objects.count()
        stats['interview_completed'] = InterviewSession.objects.filter(final_report__isnull=False).count()
        
        return ApiResponse.success(data=stats)
