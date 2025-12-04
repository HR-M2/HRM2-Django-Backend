"""
简历数据管理视图模块。
"""
import logging
from apps.common.mixins import SafeAPIView
from apps.common.response import APIResponse
from apps.common.pagination import paginate_queryset
from apps.common.utils import generate_hash

from ..models import ResumeData
from ..serializers import ResumeDataSerializer

logger = logging.getLogger(__name__)


class ResumeDataView(SafeAPIView):
    """
    简历数据管理API
    GET: 获取简历数据列表
    POST: 创建新的简历数据
    """
    
    def handle_get(self, request):
        """获取简历数据列表，支持过滤和分页。"""
        candidate_name = request.GET.get('candidate_name')
        position_title = request.GET.get('position_title')
        
        queryset = ResumeData.objects.all()
        
        if candidate_name:
            queryset = queryset.filter(candidate_name__icontains=candidate_name)
        if position_title:
            queryset = queryset.filter(position_title__icontains=position_title)
        
        # 分页
        items, pagination = paginate_queryset(queryset, request)
        
        # 构建响应
        result = []
        for data in items:
            item = {
                "id": str(data.id),
                "created_at": data.created_at.isoformat(),
                "position_title": data.position_title,
                "candidate_name": data.candidate_name,
                "screening_score": data.screening_score,
                "resume_file_hash": data.resume_file_hash,
                "report_md_url": data.report_md_file.url if data.report_md_file else None,
                "report_json_url": data.report_json_file.url if data.report_json_file else None,
            }
            
            # 如果存在则添加视频分析信息
            if data.video_analysis:
                item["video_analysis"] = {
                    "video_id": str(data.video_analysis.id),
                    "video_name": data.video_analysis.video_name,
                    "status": data.video_analysis.status,
                    "confidence_score": data.video_analysis.confidence_score,
                }
            
            result.append(item)
        
        return APIResponse.paginated(result, pagination['total'], pagination['page'], pagination['page_size'])
    
    def handle_post(self, request):
        """创建新的简历数据记录。"""
        position_title = self.get_param(request, 'position_title', required=True)
        position_details = self.get_param(request, 'position_details', default={})
        candidate_name = self.get_param(request, 'candidate_name', required=True)
        resume_content = self.get_param(request, 'resume_content', required=True)
        
        resume_data = ResumeData.objects.create(
            position_title=position_title,
            position_details=position_details,
            candidate_name=candidate_name,
            resume_content=resume_content,
            resume_file_hash=generate_hash(resume_content)
        )
        
        return APIResponse.created(
            data={"id": str(resume_data.id)},
            message="简历数据创建成功"
        )


class ResumeDataDetailView(SafeAPIView):
    """
    简历数据详情API
    GET: 获取简历数据详情
    """
    
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
            "scores": scores,
            "summary": resume_data.screening_summary,
            "resume_content": resume_data.resume_content,
            "json_report_content": resume_data.json_report_content,
            "report_json_url": resume_data.report_json_file.url if resume_data.report_json_file else None,
            "video_analysis_id": str(resume_data.video_analysis.id) if resume_data.video_analysis else None,
        }
        
        return APIResponse.success({"report": data})
