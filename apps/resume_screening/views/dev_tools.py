"""
开发测试工具视图模块。
提供开发辅助API，如生成随机简历等。
"""
import logging

from drf_spectacular.utils import extend_schema

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.exceptions import ValidationException
from apps.common.schemas import (
    api_response,
    GenerateResumesRequestSerializer, GenerateResumesResponseSerializer,
)
from apps.resume.models import Resume
from apps.position_settings.models import Position

logger = logging.getLogger(__name__)


class GenerateRandomResumesView(SafeAPIView):
    """
    生成随机简历API
    POST: 根据岗位要求生成随机简历并添加到简历库
    """
    
    @extend_schema(
        summary="生成随机简历",
        description="根据岗位要求使用AI生成随机简历并添加到简历库（开发测试用）",
        request=GenerateResumesRequestSerializer,
        responses={200: api_response(GenerateResumesResponseSerializer(), "GenerateResumes")},
        tags=["screening"],
    )
    def handle_post(self, request):
        """生成随机简历并添加到简历库"""
        from services.agents import get_dev_tools_service
        
        data = request.data
        position_data = data.get('position', {})
        count = data.get('count', 5)
        
        if not position_data:
            raise ValidationException("请提供岗位信息")
        
        if not position_data.get('position'):
            raise ValidationException("请提供岗位名称")
        
        # 限制数量
        count = max(1, min(20, int(count)))
        
        try:
            service = get_dev_tools_service()
            resumes = service.generate_batch_resumes(position_data, count)
            
            # 获取或创建岗位
            position_title = position_data.get('position', '未指定岗位')
            position, _ = Position.objects.get_or_create(
                title=position_title,
                defaults={'requirements': position_data}
            )
            
            # 添加到简历库
            added_resumes = []
            skipped_resumes = []
            
            for resume in resumes:
                # 检查哈希是否已存在
                if Resume.objects.filter(file_hash=resume['file_hash']).exists():
                    skipped_resumes.append({
                        'filename': resume['name'],
                        'reason': '哈希值已存在'
                    })
                    continue
                
                # 创建简历记录
                resume_entry = Resume.objects.create(
                    filename=resume['name'],
                    file_hash=resume['file_hash'],
                    file_size=len(resume['content'].encode('utf-8')),
                    file_type='text/plain',
                    content=resume['content'],
                    candidate_name=resume['candidate_name'],
                    position=position,
                    status=Resume.Status.PENDING,
                    notes=f"由开发测试工具自动生成"
                )
                
                added_resumes.append({
                    'id': str(resume_entry.id),
                    'filename': resume_entry.filename,
                    'candidate_name': resume_entry.candidate_name
                })
            
            return ApiResponse.success(
                data={
                    'added': added_resumes,
                    'skipped': skipped_resumes,
                    'added_count': len(added_resumes),
                    'skipped_count': len(skipped_resumes),
                    'requested_count': count
                },
                message=f'成功生成 {len(added_resumes)} 份简历'
            )
            
        except Exception as e:
            logger.error(f"Failed to generate resumes: {e}")
            raise ValidationException(f"生成简历失败: {str(e)}")
