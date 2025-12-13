"""
开发测试工具视图模块。
提供开发辅助API，如生成随机简历等。
"""
import logging

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.exceptions import ValidationException
from apps.resume_library.models import ResumeLibrary

logger = logging.getLogger(__name__)


class GenerateRandomResumesView(SafeAPIView):
    """
    生成随机简历API
    POST: 根据岗位要求生成随机简历并添加到简历库
    """
    
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
            
            # 添加到简历库
            added_resumes = []
            skipped_resumes = []
            
            for resume in resumes:
                # 检查哈希是否已存在
                if ResumeLibrary.objects.filter(file_hash=resume['file_hash']).exists():
                    skipped_resumes.append({
                        'filename': resume['name'],
                        'reason': '哈希值已存在'
                    })
                    continue
                
                # 创建简历库记录
                library_entry = ResumeLibrary.objects.create(
                    filename=resume['name'],
                    file_hash=resume['file_hash'],
                    file_size=len(resume['content'].encode('utf-8')),
                    file_type='text/plain',
                    content=resume['content'],
                    candidate_name=resume['candidate_name'],
                    is_screened=False,
                    is_assigned=False,
                    notes=f"由开发测试工具自动生成，目标岗位：{position_data.get('position', '未知')}"
                )
                
                added_resumes.append({
                    'id': str(library_entry.id),
                    'filename': library_entry.filename,
                    'candidate_name': library_entry.candidate_name
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
