"""
简历库服务层模块。

提供简历库的业务逻辑接口，供其他模块调用。
"""
import re
import logging
from typing import Optional, List, Dict, Any
from django.db import models

from apps.common.utils import generate_hash
from .models import ResumeLibrary

logger = logging.getLogger(__name__)


class LibraryService:
    """
    简历库服务类。
    
    提供简历库的业务逻辑接口，用于模块间通信。
    """
    
    @staticmethod
    def get_resume_by_id(resume_id: str) -> Optional[ResumeLibrary]:
        """
        根据ID获取简历。
        
        Args:
            resume_id: 简历ID
            
        Returns:
            ResumeLibrary 实例，不存在返回 None
        """
        try:
            return ResumeLibrary.objects.get(id=resume_id)
        except ResumeLibrary.DoesNotExist:
            return None
    
    @staticmethod
    def get_resumes_by_ids(resume_ids: List[str]) -> List[ResumeLibrary]:
        """
        根据ID列表批量获取简历。
        
        Args:
            resume_ids: 简历ID列表
            
        Returns:
            ResumeLibrary 实例列表
        """
        return list(ResumeLibrary.objects.filter(id__in=resume_ids))
    
    @staticmethod
    def get_resume_by_hash(file_hash: str) -> Optional[ResumeLibrary]:
        """
        根据文件哈希值获取简历。
        
        Args:
            file_hash: 文件哈希值
            
        Returns:
            ResumeLibrary 实例，不存在返回 None
        """
        try:
            return ResumeLibrary.objects.get(file_hash=file_hash)
        except ResumeLibrary.DoesNotExist:
            return None
    
    @staticmethod
    def mark_as_screened(resume_id: str) -> bool:
        """
        标记简历已筛选。
        
        Args:
            resume_id: 简历ID
            
        Returns:
            是否成功
        """
        try:
            resume = ResumeLibrary.objects.get(id=resume_id)
            resume.is_screened = True
            resume.save(update_fields=['is_screened', 'updated_at'])
            return True
        except ResumeLibrary.DoesNotExist:
            return False
    
    @staticmethod
    def mark_as_assigned(resume_id: str) -> bool:
        """
        标记简历已分配岗位。
        
        Args:
            resume_id: 简历ID
            
        Returns:
            是否成功
        """
        try:
            resume = ResumeLibrary.objects.get(id=resume_id)
            resume.is_assigned = True
            resume.save(update_fields=['is_assigned', 'updated_at'])
            return True
        except ResumeLibrary.DoesNotExist:
            return False
    
    @staticmethod
    def batch_mark_as_screened(resume_ids: List[str]) -> int:
        """
        批量标记简历已筛选。
        
        Args:
            resume_ids: 简历ID列表
            
        Returns:
            更新的记录数
        """
        return ResumeLibrary.objects.filter(id__in=resume_ids).update(is_screened=True)
    
    @staticmethod
    def check_hashes_exist(hashes: List[str]) -> Dict[str, bool]:
        """
        检查哈希值列表中哪些已存在。
        
        Args:
            hashes: 哈希值列表
            
        Returns:
            哈希值到是否存在的映射
        """
        existing = set(
            ResumeLibrary.objects.filter(file_hash__in=hashes)
            .values_list('file_hash', flat=True)
        )
        return {h: h in existing for h in hashes}
    
    @staticmethod
    def upload_resume(
        filename: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[Optional[ResumeLibrary], Optional[str]]:
        """
        上传单份简历。
        
        Args:
            filename: 文件名
            content: 简历内容
            metadata: 元数据（可选，包含 size, type 等）
            
        Returns:
            (ResumeLibrary 实例, 错误信息)
            成功时错误信息为 None，失败时实例为 None
        """
        if not content:
            return None, "内容为空"
        
        metadata = metadata or {}
        
        # 计算哈希值
        file_hash = generate_hash(content)
        
        # 检查是否已存在
        if ResumeLibrary.objects.filter(file_hash=file_hash).exists():
            return None, "简历已存在"
        
        # 尝试提取候选人姓名
        candidate_name = LibraryService._extract_candidate_name(content, filename)
        
        # 创建记录
        resume = ResumeLibrary.objects.create(
            filename=filename,
            file_hash=file_hash,
            file_size=metadata.get('size', len(content)),
            file_type=metadata.get('type', ''),
            content=content,
            candidate_name=candidate_name
        )
        
        return resume, None
    
    @staticmethod
    def _extract_candidate_name(content: str, filename: str) -> Optional[str]:
        """
        从简历内容或文件名中提取候选人姓名。
        
        Args:
            content: 简历内容
            filename: 文件名
            
        Returns:
            候选人姓名，无法提取返回 None
        """
        # 移除扩展名
        name_from_file = re.sub(r'\.[^.]+$', '', filename)
        
        # 常见的简历文件名模式
        patterns = [
            r'^([\u4e00-\u9fa5]{2,4})[-_]简历',  # 张三_简历（中文名+分隔符+简历）
            r'简历[-_]([\u4e00-\u9fa5]{2,4})$',  # 简历_张三
            r'^([\u4e00-\u9fa5]{2,4})[-_]?resume',
            r'resume[-_]?([\u4e00-\u9fa5]{2,4})$',
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
    
    @staticmethod
    def search_resumes(
        keyword: Optional[str] = None,
        is_screened: Optional[bool] = None,
        is_assigned: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[ResumeLibrary], int]:
        """
        搜索简历库。
        
        Args:
            keyword: 关键词（搜索文件名和候选人姓名）
            is_screened: 是否已筛选
            is_assigned: 是否已分配
            page: 页码
            page_size: 每页数量
            
        Returns:
            (简历列表, 总数)
        """
        queryset = ResumeLibrary.objects.all()
        
        # 关键词搜索
        if keyword:
            queryset = queryset.filter(
                models.Q(filename__icontains=keyword) |
                models.Q(candidate_name__icontains=keyword)
            )
        
        # 筛选状态过滤
        if is_screened is not None:
            queryset = queryset.filter(is_screened=is_screened)
        
        if is_assigned is not None:
            queryset = queryset.filter(is_assigned=is_assigned)
        
        # 计算总数
        total = queryset.count()
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        resumes = list(queryset[start:end])
        
        return resumes, total
    
    @staticmethod
    def delete_resume(resume_id: str) -> bool:
        """
        删除单份简历。
        
        Args:
            resume_id: 简历ID
            
        Returns:
            是否成功
        """
        try:
            resume = ResumeLibrary.objects.get(id=resume_id)
            resume.delete()
            return True
        except ResumeLibrary.DoesNotExist:
            return False
    
    @staticmethod
    def batch_delete(resume_ids: List[str]) -> int:
        """
        批量删除简历。
        
        Args:
            resume_ids: 简历ID列表
            
        Returns:
            删除的记录数
        """
        deleted_count, _ = ResumeLibrary.objects.filter(id__in=resume_ids).delete()
        return deleted_count
