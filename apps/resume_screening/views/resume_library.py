"""
简历库视图模块 - 管理上传的原始简历
"""
import logging
from django.db import models
from django.http import JsonResponse

from apps.common.mixins import SafeAPIView
from apps.common.utils import generate_hash
from apps.common.exceptions import ValidationException, NotFoundException

from ..models import ResumeLibrary

logger = logging.getLogger(__name__)


class ResumeLibraryListView(SafeAPIView):
    """
    简历库列表API
    GET: 获取简历库列表（支持分页和筛选）
    POST: 上传简历到简历库
    """
    
    def handle_get(self, request):
        """获取简历库列表"""
        # 分页参数
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        
        # 筛选参数
        keyword = request.GET.get('keyword', '')
        is_screened = request.GET.get('is_screened')
        is_assigned = request.GET.get('is_assigned')
        
        queryset = ResumeLibrary.objects.all()
        
        # 关键词搜索
        if keyword:
            queryset = queryset.filter(
                models.Q(filename__icontains=keyword) |
                models.Q(candidate_name__icontains=keyword)
            )
        
        # 筛选状态过滤
        if is_screened is not None:
            queryset = queryset.filter(is_screened=is_screened.lower() == 'true')
        
        if is_assigned is not None:
            queryset = queryset.filter(is_assigned=is_assigned.lower() == 'true')
        
        # 分页
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        resumes = queryset[start:end]
        
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
        
        return JsonResponse({
            'code': 200,
            'message': '成功',
            'data': {
                'resumes': result,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })
    
    def handle_post(self, request):
        """上传简历到简历库（支持批量上传）"""
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
            
            if not content:
                skipped.append({'filename': filename, 'reason': '内容为空'})
                continue
            
            # 计算哈希值
            file_hash = generate_hash(content)
            
            # 检查是否已存在
            if ResumeLibrary.objects.filter(file_hash=file_hash).exists():
                skipped.append({'filename': filename, 'reason': '简历已存在'})
                continue
            
            # 尝试提取候选人姓名（简单提取）
            candidate_name = self._extract_candidate_name(content, filename)
            
            # 创建记录
            resume = ResumeLibrary.objects.create(
                filename=filename,
                file_hash=file_hash,
                file_size=metadata.get('size', len(content)),
                file_type=metadata.get('type', ''),
                content=content,
                candidate_name=candidate_name
            )
            
            uploaded.append({
                'id': str(resume.id),
                'filename': resume.filename,
                'candidate_name': resume.candidate_name
            })
        
        return JsonResponse({
            'code': 200,
            'message': f'成功上传 {len(uploaded)} 份简历，跳过 {len(skipped)} 份',
            'data': {
                'uploaded': uploaded,
                'skipped': skipped,
                'uploaded_count': len(uploaded),
                'skipped_count': len(skipped)
            }
        })
    
    def _extract_candidate_name(self, content: str, filename: str) -> str:
        """从简历内容或文件名中提取候选人姓名"""
        # 首先尝试从文件名提取
        import re
        
        # 移除扩展名
        name_from_file = re.sub(r'\.[^.]+$', '', filename)
        
        # 常见的简历文件名模式：姓名_简历、简历_姓名、姓名-简历 等
        patterns = [
            r'^(.{2,4})[-_]?简历',  # 张三_简历
            r'简历[-_]?(.{2,4})$',  # 简历_张三
            r'^(.{2,4})[-_]?resume',
            r'resume[-_]?(.{2,4})$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name_from_file, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 如果文件名只有2-4个字符，可能就是姓名
        if 2 <= len(name_from_file) <= 4 and re.match(r'^[\u4e00-\u9fa5]+$', name_from_file):
            return name_from_file
        
        # 尝试从内容中提取（取前几行）
        lines = content.split('\n')[:10]
        for line in lines:
            line = line.strip()
            # 匹配"姓名：xxx"模式
            match = re.search(r'姓\s*名[：:]\s*(.{2,4})', line)
            if match:
                return match.group(1).strip()
            # 匹配开头的中文姓名
            if re.match(r'^[\u4e00-\u9fa5]{2,4}$', line):
                return line
        
        return None


class ResumeLibraryDetailView(SafeAPIView):
    """
    简历库详情API
    GET: 获取简历详情
    PUT: 更新简历信息
    DELETE: 删除简历
    """
    
    def handle_get(self, request, resume_id):
        """获取简历详情"""
        try:
            resume = ResumeLibrary.objects.get(id=resume_id)
        except ResumeLibrary.DoesNotExist:
            raise NotFoundException("简历不存在")
        
        return JsonResponse({
            'code': 200,
            'message': '成功',
            'data': {
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
            }
        })
    
    def handle_put(self, request, resume_id):
        """更新简历信息"""
        try:
            resume = ResumeLibrary.objects.get(id=resume_id)
        except ResumeLibrary.DoesNotExist:
            raise NotFoundException("简历不存在")
        
        data = request.data
        
        # 可更新的字段
        if 'candidate_name' in data:
            resume.candidate_name = data['candidate_name']
        if 'notes' in data:
            resume.notes = data['notes']
        
        resume.save()
        
        return JsonResponse({
            'code': 200,
            'message': '更新成功',
            'data': {'id': str(resume.id)}
        })
    
    def handle_delete(self, request, resume_id):
        """删除简历"""
        try:
            resume = ResumeLibrary.objects.get(id=resume_id)
        except ResumeLibrary.DoesNotExist:
            raise NotFoundException("简历不存在")
        
        resume.delete()
        
        return JsonResponse({
            'code': 200,
            'message': '删除成功'
        })


class ResumeLibraryBatchDeleteView(SafeAPIView):
    """批量删除简历"""
    
    def handle_post(self, request):
        """批量删除简历"""
        resume_ids = self.get_param(request, 'resume_ids', required=True)
        
        if not isinstance(resume_ids, list):
            raise ValidationException("resume_ids 必须是数组")
        
        deleted_count = ResumeLibrary.objects.filter(id__in=resume_ids).delete()[0]
        
        return JsonResponse({
            'code': 200,
            'message': f'成功删除 {deleted_count} 份简历'
        })


class ResumeLibraryCheckHashView(SafeAPIView):
    """检查简历哈希值是否已存在"""
    
    def handle_post(self, request):
        """检查哈希值列表"""
        hashes = self.get_param(request, 'hashes', required=True)
        
        if not isinstance(hashes, list):
            raise ValidationException("hashes 必须是数组")
        
        # 查询已存在的哈希值
        existing = set(
            ResumeLibrary.objects.filter(file_hash__in=hashes)
            .values_list('file_hash', flat=True)
        )
        
        result = {h: h in existing for h in hashes}
        
        return JsonResponse({
            'code': 200,
            'message': '成功',
            'data': {
                'exists': result,
                'existing_count': len(existing)
            }
        })
