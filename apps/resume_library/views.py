"""
简历库视图模块。

提供简历库的 CRUD 操作 API。
"""
import logging
from django.db import models

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.exceptions import ValidationException, NotFoundException

from .models import ResumeLibrary
from .services import LibraryService

logger = logging.getLogger(__name__)


class LibraryListView(SafeAPIView):
    """
    简历库列表API。
    
    GET: 获取简历库列表（支持分页和筛选）
    POST: 上传简历到简历库
    """
    
    def handle_get(self, request):
        """获取简历库列表。"""
        # 分页参数
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        
        # 筛选参数
        keyword = request.GET.get('keyword', '')
        is_screened_str = request.GET.get('is_screened')
        is_assigned_str = request.GET.get('is_assigned')
        
        # 转换布尔参数
        is_screened = None
        if is_screened_str is not None:
            is_screened = is_screened_str.lower() == 'true'
        
        is_assigned = None
        if is_assigned_str is not None:
            is_assigned = is_assigned_str.lower() == 'true'
        
        # 使用服务层搜索
        resumes, total = LibraryService.search_resumes(
            keyword=keyword or None,
            is_screened=is_screened,
            is_assigned=is_assigned,
            page=page,
            page_size=page_size
        )
        
        # 构建响应
        result = []
        for resume in resumes:
            result.append({
                'id': str(resume.id),
                'filename': resume.filename,
                'file_hash': resume.file_hash[:8],  # 只返回前8位
                'file_size': resume.file_size,
                'file_type': resume.file_type,
                'candidate_name': resume.candidate_name,
                'is_screened': resume.is_screened,
                'is_assigned': resume.is_assigned,
                'notes': resume.notes,
                'created_at': resume.created_at.isoformat(),
                'content_preview': resume.content[:200] + '...' if len(resume.content) > 200 else resume.content
            })
        
        return ApiResponse.paginated(
            items=result,
            total=total,
            page=page,
            page_size=page_size
        )
    
    def handle_post(self, request):
        """上传简历到简历库（支持批量上传）。"""
        resumes = self.get_param(request, 'resumes', required=True)
        
        if not isinstance(resumes, list):
            raise ValidationException("resumes 必须是数组")
        
        if len(resumes) == 0:
            raise ValidationException("至少需要上传一份简历")
        
        if len(resumes) > 50:
            raise ValidationException("单次最多上传50份简历")
        
        uploaded = []
        skipped = []
        
        for resume_item in resumes:
            filename = resume_item.get('name', '')
            content = resume_item.get('content', '')
            metadata = resume_item.get('metadata', {})
            
            resume, error = LibraryService.upload_resume(filename, content, metadata)
            
            if resume:
                uploaded.append({
                    'id': str(resume.id),
                    'filename': resume.filename,
                    'candidate_name': resume.candidate_name
                })
            else:
                skipped.append({'filename': filename, 'reason': error})
        
        return ApiResponse.success(
            data={
                'uploaded': uploaded,
                'skipped': skipped,
                'uploaded_count': len(uploaded),
                'skipped_count': len(skipped)
            },
            message=f'成功上传 {len(uploaded)} 份简历，跳过 {len(skipped)} 份'
        )


class LibraryDetailView(SafeAPIView):
    """
    简历库详情API。
    
    GET: 获取简历详情
    PUT: 更新简历信息
    DELETE: 删除简历
    """
    
    def handle_get(self, request, id):
        """获取简历详情。"""
        resume = LibraryService.get_resume_by_id(str(id))
        if not resume:
            raise NotFoundException("简历不存在")
        
        return ApiResponse.success(data={
            'id': str(resume.id),
            'filename': resume.filename,
            'file_hash': resume.file_hash,
            'file_size': resume.file_size,
            'file_type': resume.file_type,
            'content': resume.content,
            'candidate_name': resume.candidate_name,
            'is_screened': resume.is_screened,
            'is_assigned': resume.is_assigned,
            'notes': resume.notes,
            'created_at': resume.created_at.isoformat(),
            'updated_at': resume.updated_at.isoformat()
        })
    
    def handle_put(self, request, id):
        """更新简历信息。"""
        resume = LibraryService.get_resume_by_id(str(id))
        if not resume:
            raise NotFoundException("简历不存在")
        
        data = request.data
        
        # 可更新的字段
        if 'candidate_name' in data:
            resume.candidate_name = data['candidate_name']
        if 'notes' in data:
            resume.notes = data['notes']
        
        resume.save()
        
        return ApiResponse.success(
            data={'id': str(resume.id)},
            message='更新成功'
        )
    
    def handle_delete(self, request, id):
        """删除简历。"""
        if not LibraryService.delete_resume(str(id)):
            raise NotFoundException("简历不存在")
        
        return ApiResponse.success(message='删除成功')


class LibraryBatchDeleteView(SafeAPIView):
    """
    批量删除简历API。
    
    POST: 批量删除简历
    """
    
    def handle_post(self, request):
        """批量删除简历。"""
        resume_ids = self.get_param(request, 'resume_ids', required=True)
        
        if not isinstance(resume_ids, list):
            raise ValidationException("resume_ids 必须是数组")
        
        deleted_count = LibraryService.batch_delete(resume_ids)
        
        return ApiResponse.success(
            data={'deleted_count': deleted_count},
            message=f'成功删除 {deleted_count} 份简历'
        )


class LibraryCheckHashView(SafeAPIView):
    """
    检查简历哈希值是否已存在API。
    
    POST: 检查哈希值列表
    """
    
    def handle_post(self, request):
        """检查哈希值列表。"""
        hashes = self.get_param(request, 'hashes', required=True)
        
        if not isinstance(hashes, list):
            raise ValidationException("hashes 必须是数组")
        
        result = LibraryService.check_hashes_exist(hashes)
        existing_count = sum(1 for v in result.values() if v)
        
        return ApiResponse.success(data={
            'exists': result,
            'existing_count': existing_count
        })
