"""
简历管理服务层模块。

数据库简化重构 - Phase 7:
- 实现简历状态转换逻辑
- 实现筛选结果更新逻辑
- 提供统一的简历操作接口
"""
import logging
from typing import Dict, List, Optional, Tuple
from django.db import transaction
from django.utils import timezone

from apps.common.utils import generate_hash, extract_name_from_filename
from apps.common.exceptions import ValidationException, NotFoundException

logger = logging.getLogger(__name__)


class ResumeService:
    """简历管理服务类。"""
    
    @classmethod
    def get_resume_by_id(cls, resume_id: str):
        """
        根据ID获取简历。
        
        参数:
            resume_id: 简历UUID
            
        返回:
            Resume实例
            
        异常:
            NotFoundException: 如果简历不存在
        """
        from .models import Resume
        
        try:
            return Resume.objects.get(id=resume_id)
        except Resume.DoesNotExist:
            raise NotFoundException(f"简历不存在: {resume_id}")
    
    @classmethod
    def get_resume_by_hash(cls, file_hash: str):
        """
        根据文件哈希获取简历。
        
        参数:
            file_hash: 文件哈希值
            
        返回:
            Resume实例或None
        """
        from .models import Resume
        
        return Resume.objects.filter(file_hash=file_hash).first()
    
    @classmethod
    def create_resume(
        cls,
        filename: str,
        content: str,
        candidate_name: str = None,
        file_size: int = 0,
        file_type: str = "text/plain",
        position_id: str = None
    ) -> Tuple['Resume', bool]:
        """
        创建或获取已存在的简历。
        
        参数:
            filename: 文件名
            content: 简历内容
            candidate_name: 候选人姓名（可选，自动从文件名提取）
            file_size: 文件大小
            file_type: 文件类型
            position_id: 岗位ID（可选）
            
        返回:
            元组 (Resume实例, 是否为新创建)
        """
        from .models import Resume
        from apps.position_settings.models import Position
        
        # 计算哈希
        file_hash = generate_hash(content)
        
        # 检查是否已存在
        existing = cls.get_resume_by_hash(file_hash)
        if existing:
            logger.info(f"简历已存在（哈希: {file_hash[:8]}...）")
            return existing, False
        
        # 提取候选人名称
        if not candidate_name:
            candidate_name = extract_name_from_filename(filename)
        
        # 获取岗位（如果指定）
        position = None
        if position_id:
            try:
                position = Position.objects.get(id=position_id)
            except Position.DoesNotExist:
                logger.warning(f"岗位不存在: {position_id}")
        
        # 创建简历
        resume = Resume.objects.create(
            filename=filename,
            file_hash=file_hash,
            file_size=file_size,
            file_type=file_type,
            candidate_name=candidate_name,
            content=content,
            position=position,
            status=Resume.Status.PENDING
        )
        
        logger.info(f"创建新简历: {resume.id} ({candidate_name})")
        return resume, True
    
    @classmethod
    @transaction.atomic
    def update_status(cls, resume_id: str, new_status: str) -> 'Resume':
        """
        更新简历状态。
        
        参数:
            resume_id: 简历UUID
            new_status: 新状态 (pending/screened/interviewing/analyzed)
            
        返回:
            更新后的Resume实例
            
        异常:
            ValidationException: 如果状态值无效
        """
        from .models import Resume
        
        resume = cls.get_resume_by_id(resume_id)
        
        valid_statuses = [choice[0] for choice in Resume.Status.choices]
        if new_status not in valid_statuses:
            raise ValidationException(f"无效状态: {new_status}，有效值: {valid_statuses}")
        
        old_status = resume.status
        resume.status = new_status
        resume.save(update_fields=['status', 'updated_at'])
        
        logger.info(f"简历 {resume_id} 状态: {old_status} -> {new_status}")
        return resume
    
    @classmethod
    @transaction.atomic
    def set_screening_result(
        cls,
        resume_id: str,
        result: Dict,
        report_md: str = None,
        update_status: bool = True
    ) -> 'Resume':
        """
        设置简历筛选结果。
        
        参数:
            resume_id: 简历UUID
            result: 筛选结果字典，包含 scores, summary 等
            report_md: Markdown格式的筛选报告（可选）
            update_status: 是否同时更新状态为 SCREENED（默认True）
            
        返回:
            更新后的Resume实例
        """
        from .models import Resume
        
        resume = cls.get_resume_by_id(resume_id)
        
        resume.screening_result = result
        if report_md:
            resume.screening_report = report_md
        
        if update_status:
            resume.status = Resume.Status.SCREENED
        
        resume.save(update_fields=['screening_result', 'screening_report', 'status', 'updated_at'])
        
        logger.info(f"简历 {resume_id} 筛选结果已更新，分数: {result.get('scores', {}).get('comprehensive_score', 'N/A')}")
        return resume
    
    @classmethod
    @transaction.atomic
    def assign_to_position(cls, resume_id: str, position_id: str) -> 'Resume':
        """
        将简历分配到岗位。
        
        参数:
            resume_id: 简历UUID
            position_id: 岗位UUID
            
        返回:
            更新后的Resume实例
        """
        from .models import Resume
        from apps.position_settings.models import Position
        
        resume = cls.get_resume_by_id(resume_id)
        
        try:
            position = Position.objects.get(id=position_id)
        except Position.DoesNotExist:
            raise NotFoundException(f"岗位不存在: {position_id}")
        
        resume.position = position
        resume.save(update_fields=['position', 'updated_at'])
        
        logger.info(f"简历 {resume_id} 已分配到岗位: {position.title}")
        return resume
    
    @classmethod
    @transaction.atomic
    def unassign_position(cls, resume_id: str) -> 'Resume':
        """
        取消简历的岗位分配。
        
        参数:
            resume_id: 简历UUID
            
        返回:
            更新后的Resume实例
        """
        resume = cls.get_resume_by_id(resume_id)
        
        old_position = resume.position
        resume.position = None
        resume.save(update_fields=['position', 'updated_at'])
        
        if old_position:
            logger.info(f"简历 {resume_id} 已取消岗位分配（原岗位: {old_position.title}）")
        
        return resume
    
    @classmethod
    @transaction.atomic
    def batch_assign_to_position(cls, resume_ids: List[str], position_id: str) -> List['Resume']:
        """
        批量将简历分配到岗位。
        
        参数:
            resume_ids: 简历UUID列表
            position_id: 岗位UUID
            
        返回:
            更新后的Resume实例列表
        """
        from .models import Resume
        from apps.position_settings.models import Position
        
        try:
            position = Position.objects.get(id=position_id)
        except Position.DoesNotExist:
            raise NotFoundException(f"岗位不存在: {position_id}")
        
        resumes = Resume.objects.filter(id__in=resume_ids)
        updated_count = resumes.update(position=position, updated_at=timezone.now())
        
        logger.info(f"{updated_count} 份简历已分配到岗位: {position.title}")
        return list(resumes)
    
    @classmethod
    def get_statistics(cls, position_id: str = None) -> Dict:
        """
        获取简历统计数据。
        
        参数:
            position_id: 可选的岗位ID过滤
            
        返回:
            统计数据字典
        """
        from .models import Resume
        from django.db.models import Count
        
        queryset = Resume.objects.all()
        if position_id:
            queryset = queryset.filter(position_id=position_id)
        
        # 按状态统计
        status_counts = queryset.values('status').annotate(count=Count('id'))
        status_dict = {item['status']: item['count'] for item in status_counts}
        
        total = queryset.count()
        assigned = queryset.filter(position__isnull=False).count()
        
        return {
            'total': total,
            'assigned': assigned,
            'unassigned': total - assigned,
            'pending': status_dict.get('pending', 0),
            'screened': status_dict.get('screened', 0),
            'interviewing': status_dict.get('interviewing', 0),
            'analyzed': status_dict.get('analyzed', 0),
        }


class ResumeStatusTransition:
    """简历状态转换管理器。"""
    
    # 有效的状态转换路径
    VALID_TRANSITIONS = {
        'pending': ['screened', 'interviewing'],
        'screened': ['interviewing', 'analyzed', 'pending'],
        'interviewing': ['analyzed', 'screened'],
        'analyzed': ['interviewing', 'screened'],
    }
    
    @classmethod
    def can_transition(cls, current_status: str, new_status: str) -> bool:
        """检查状态转换是否有效。"""
        valid_next = cls.VALID_TRANSITIONS.get(current_status, [])
        return new_status in valid_next
    
    @classmethod
    def transition_to_screened(cls, resume_id: str, result: Dict, report_md: str = None):
        """
        状态转换：-> screened（已筛选）
        
        在筛选任务完成后调用。
        """
        return ResumeService.set_screening_result(resume_id, result, report_md)
    
    @classmethod
    def transition_to_interviewing(cls, resume_id: str):
        """
        状态转换：-> interviewing（面试中）
        
        在创建面试会话时调用。
        """
        from .models import Resume
        return ResumeService.update_status(resume_id, Resume.Status.INTERVIEWING)
    
    @classmethod
    def transition_to_analyzed(cls, resume_id: str):
        """
        状态转换：-> analyzed（已分析）
        
        在综合分析完成后调用。
        """
        from .models import Resume
        return ResumeService.update_status(resume_id, Resume.Status.ANALYZED)
