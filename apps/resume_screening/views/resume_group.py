"""
简历组管理视图模块 - 与原版 RecruitmentSystemAPI 返回格式保持一致。
"""
import logging

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.pagination import paginate_queryset
from apps.common.exceptions import ValidationException

from ..models import ResumeGroup
from ..services import GroupService
from ..serializers import CreateResumeGroupSerializer

logger = logging.getLogger(__name__)


class ResumeGroupListView(SafeAPIView):
    """
    简历组列表API
    GET: 获取简历组列表
    """
    
    def handle_get(self, request):
        """获取简历组列表，支持过滤和分页。"""
        # 获取查询参数
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 10)), 100)
        position_title = request.GET.get('position_title')
        filter_status = request.GET.get('status')
        include_resumes = request.GET.get('include_resumes', 'false').lower() == 'true'
        
        queryset = ResumeGroup.objects.all().order_by('-created_at')
        
        if position_title:
            queryset = queryset.filter(position_title__icontains=position_title)
        if filter_status:
            queryset = queryset.filter(status=filter_status)
        
        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        groups = queryset[start:end]
        
        # 构建响应数据 - 与原版格式完全一致
        groups_data = []
        for group in groups:
            # 根据视频分析更新状态
            GroupService.update_status_based_on_video(str(group.id))
            group.refresh_from_db()
            
            group_data = {
                "id": str(group.id),
                "group_name": group.group_name,
                "position_title": group.position_title,
                "description": group.description,
                "resume_count": group.resumes.count(),
                "status": group.status,
                "created_at": group.created_at.isoformat()
            }
            
            if include_resumes:
                group_data["resumes"] = self._get_resumes(group)
            
            groups_data.append(group_data)
        
        # 返回与原版完全一致的格式
        return ApiResponse.success(data={
            "groups": groups_data,
            "total": total,
            "page": page,
            "page_size": page_size
        })
    
    def _get_resumes(self, group):
        """获取组内简历。"""
        resumes = []
        for r in group.resumes.all():
            resume_data = {
                "id": str(r.id),
                "candidate_name": r.candidate_name,
                "position_title": r.position_title,
                "screening_score": r.screening_score,
                "screening_summary": r.screening_summary,
                "resume_content": r.resume_content,
                "created_at": r.created_at.isoformat(),
                "report_md_url": r.report_md_file.url if r.report_md_file else None,
                "report_json_url": r.report_json_file.url if r.report_json_file else None,
            }
            resumes.append(resume_data)
        return resumes


class ResumeGroupDetailView(SafeAPIView):
    """
    简历组详情API
    GET: 获取简历组详情
    """
    
    def handle_get(self, request, group_id):
        """获取简历组详情。"""
        group = self.get_object_or_404(ResumeGroup, id=group_id)
        
        # 更新状态
        GroupService.update_status_based_on_video(str(group.id))
        group.refresh_from_db()
        
        include_resumes = request.GET.get('include_resumes', 'true').lower() == 'true'
        resume_count = group.resumes.count()
        
        group_data = {
            "id": str(group.id),
            "group_name": group.group_name,
            "position_title": group.position_title,
            "description": group.description,
            "resume_count": resume_count,
            "status": group.status,
            "created_at": group.created_at.isoformat()
        }
        
        if include_resumes:
            resumes = []
            for resume in group.resumes.all():
                scores = {}
                if resume.screening_score:
                    scores = {
                        "hr_score": resume.screening_score.get("hr_score", 0),
                        "technical_score": resume.screening_score.get("technical_score", 0),
                        "manager_score": resume.screening_score.get("manager_score", 0),
                        "comprehensive_score": resume.screening_score.get("comprehensive_score", 0)
                    }
                
                resume_data = {
                    "id": str(resume.id),
                    "candidate_name": resume.candidate_name,
                    "position_title": resume.position_title,
                    "screening_score": scores,
                    "screening_summary": resume.screening_summary,
                    "json_content": resume.json_report_content,
                    "report_md_url": resume.report_md_file.url if resume.report_md_file else None,
                    "report_json_url": resume.report_json_file.url if resume.report_json_file else None,
                }
                
                if resume.video_analysis:
                    resume_data["video_analysis"] = {
                        "id": str(resume.video_analysis.id),
                        "video_name": resume.video_analysis.video_name,
                        "status": resume.video_analysis.status,
                        "analysis_result": resume.video_analysis.analysis_result,
                        "summary": resume.video_analysis.summary,
                        "confidence_score": resume.video_analysis.confidence_score,
                    }
                
                resumes.append(resume_data)
            
            group_data["resumes"] = resumes
        
        # 返回与原版完全一致的格式
        return ApiResponse.success(data={
            "group": group_data,
            "summary": {
                "total_resumes": resume_count,
                "status": group.status,
                "created_at": group.created_at.isoformat()
            }
        })


class CreateResumeGroupView(SafeAPIView):
    """
    创建简历组API
    POST: 创建新的简历组
    """
    
    def handle_post(self, request):
        """创建简历组。"""
        serializer = CreateResumeGroupSerializer(data=request.data)
        if not serializer.is_valid():
            return ApiResponse.validation_error(
                errors=serializer.errors,
                message="参数验证失败"
            )
        
        data = serializer.validated_data
        
        group = GroupService.create_group(
            group_name=data['group_name'],
            resume_data_ids=[str(id) for id in data['resume_data_ids']],
            description=data.get('description', '')
        )
        
        # 返回与原版一致的格式
        return ApiResponse.created(
            data={
                "group_id": str(group.id),
                "group_name": group.group_name,
                "resume_count": group.resume_count
            },
            message="简历组创建成功"
        )


class AddResumeToGroupView(SafeAPIView):
    """
    添加简历到组API
    POST: 向简历组添加简历
    """
    
    def handle_post(self, request):
        """向组中添加简历。"""
        group_id = self.get_param(request, 'group_id', required=True)
        resume_data_id = self.get_param(request, 'resume_data_id', required=True)
        
        group = GroupService.add_resume_to_group(group_id, resume_data_id)
        
        # 返回与原版一致的格式
        return ApiResponse.success(
            data={
                "group_id": str(group.id),
                "group_name": group.group_name,
                "resume_count": group.resume_count
            },
            message="简历成功添加到简历组"
        )


class RemoveResumeFromGroupView(SafeAPIView):
    """
    从组中移除简历API
    POST: 从简历组移除简历
    """
    
    def handle_post(self, request):
        """从组中移除简历。"""
        group_id = self.get_param(request, 'group_id', required=True)
        resume_data_id = self.get_param(request, 'resume_data_id', required=True)
        
        group = GroupService.remove_resume_from_group(group_id, resume_data_id)
        
        # 返回与原版一致的格式
        return ApiResponse.success(
            data={
                "group_id": str(group.id),
                "group_name": group.group_name,
                "resume_count": group.resume_count
            },
            message="简历成功从简历组中移除"
        )


class SetGroupStatusView(SafeAPIView):
    """
    设置简历组状态API
    POST: 更新简历组状态
    """
    
    def handle_post(self, request):
        """设置组状态。"""
        group_id = self.get_param(request, 'group_id', required=True)
        status = self.get_param(request, 'status', required=True)
        
        group = GroupService.update_group_status(group_id, status)
        
        # 返回与原版一致的格式
        return ApiResponse.success(
            data={
                "group_id": str(group.id),
                "group_name": group.group_name,
                "status": group.status
            },
            message="简历组状态更新成功"
        )
