"""
简历组管理服务模块。
"""
import logging
from typing import Dict, List, Optional, Tuple
from django.db import transaction

from apps.common.utils import calculate_position_hash
from apps.common.exceptions import ValidationException, NotFoundException

logger = logging.getLogger(__name__)


class GroupService:
    """简历组管理服务类。"""
    
    @classmethod
    def create_group(
        cls,
        group_name: str,
        resume_data_ids: List[str],
        description: str = ""
    ) -> 'ResumeGroup':
        """
        从现有简历数据创建新的简历组。
        
        参数:
            group_name: 组名称
            resume_data_ids: 要包含的ResumeData ID列表
            description: 可选的组描述
            
        返回:
            创建的ResumeGroup实例
            
        异常:
            ValidationException: 如果验证失败
            NotFoundException: 如果简历数据未找到
        """
        from ..models import ResumeData, ResumeGroup
        
        if not resume_data_ids:
            raise ValidationException("至少需要一个简历数据")
        
        # 获取简历数据记录
        resume_data_list = list(ResumeData.objects.filter(id__in=resume_data_ids))
        
        # 检查所有是否存在
        if len(resume_data_list) != len(resume_data_ids):
            existing_ids = {str(r.id) for r in resume_data_list}
            missing = [rid for rid in resume_data_ids if rid not in existing_ids]
            raise NotFoundException(f"部分简历数据不存在: {missing}")
        
        # 验证相同岗位
        first = resume_data_list[0]
        base_title = first.position_title
        base_details = first.position_details
        
        mismatched = []
        for resume_data in resume_data_list[1:]:
            if (resume_data.position_title != base_title or 
                resume_data.position_details != base_details):
                mismatched.append({
                    "id": str(resume_data.id),
                    "position_title": resume_data.position_title
                })
        
        if mismatched:
            raise ValidationException(
                "所有简历必须属于同一岗位",
                {"mismatched": mismatched, "expected": base_title}
            )
        
        # 计算岗位哈希
        position_hash = calculate_position_hash(base_title, base_details)
        
        # 检查是否存在相同岗位的组
        existing_group = ResumeGroup.objects.filter(position_hash=position_hash).first()
        
        with transaction.atomic():
            if existing_group:
                resume_group = existing_group
            else:
                resume_group = ResumeGroup.objects.create(
                    position_title=base_title,
                    position_details=base_details,
                    position_hash=position_hash,
                    group_name=group_name,
                    description=description,
                    resume_count=len(resume_data_list)
                )
            
            # 将简历与组关联
            for resume_data in resume_data_list:
                resume_data.group = resume_group
                resume_data.save()
            
            # 更新计数
            resume_group.resume_count = resume_group.resumes.count()
            resume_group.save()
        
        return resume_group
    
    @classmethod
    def add_resume_to_group(cls, group_id: str, resume_data_id: str) -> 'ResumeGroup':
        """
        向现有组添加简历。
        
        参数:
            group_id: 组ID
            resume_data_id: 要添加的简历数据ID
            
        返回:
            更新后的ResumeGroup实例
        """
        from ..models import ResumeData, ResumeGroup
        
        try:
            group = ResumeGroup.objects.get(id=group_id)
        except ResumeGroup.DoesNotExist:
            raise NotFoundException("简历组不存在")
        
        try:
            resume_data = ResumeData.objects.get(id=resume_data_id)
        except ResumeData.DoesNotExist:
            raise NotFoundException("简历数据不存在")
        
        # 检查是否已在组中
        if resume_data.group == group:
            raise ValidationException("简历数据已属于该简历组")
        
        # 检查岗位匹配
        if (resume_data.position_title != group.position_title or
            resume_data.position_details != group.position_details):
            raise ValidationException(
                "简历与简历组不属于同一岗位",
                {
                    "resume_position": resume_data.position_title,
                    "group_position": group.position_title
                }
            )
        
        with transaction.atomic():
            resume_data.group = group
            resume_data.save()
            
            group.resume_count = group.resumes.count()
            group.save()
        
        return group
    
    @classmethod
    def remove_resume_from_group(cls, group_id: str, resume_data_id: str) -> 'ResumeGroup':
        """
        从组中移除简历。
        
        参数:
            group_id: 组ID
            resume_data_id: 要移除的简历数据ID
            
        返回:
            更新后的ResumeGroup实例
        """
        from ..models import ResumeData, ResumeGroup
        
        try:
            group = ResumeGroup.objects.get(id=group_id)
        except ResumeGroup.DoesNotExist:
            raise NotFoundException("简历组不存在")
        
        try:
            resume_data = ResumeData.objects.get(id=resume_data_id)
        except ResumeData.DoesNotExist:
            raise NotFoundException("简历数据不存在")
        
        if resume_data.group != group:
            raise ValidationException("简历数据不属于该简历组")
        
        with transaction.atomic():
            resume_data.group = None
            resume_data.save()
            
            group.resume_count = group.resumes.count()
            group.save()
        
        return group
    
    @classmethod
    def update_group_status(cls, group_id: str, new_status: str) -> 'ResumeGroup':
        """
        更新简历组的状态。
        
        参数:
            group_id: 组ID
            new_status: 新的状态值
            
        返回:
            更新后的ResumeGroup实例
        """
        from ..models import ResumeGroup
        
        try:
            group = ResumeGroup.objects.get(id=group_id)
        except ResumeGroup.DoesNotExist:
            raise NotFoundException("简历组不存在")
        
        valid_statuses = [choice[0] for choice in ResumeGroup.Status.choices]
        if new_status not in valid_statuses:
            raise ValidationException(
                f"无效的状态值: {new_status}",
                {"valid_statuses": valid_statuses}
            )
        
        group.status = new_status
        group.save()
        
        return group
    
    @classmethod
    def update_status_based_on_video(cls, group_id: str) -> Tuple[bool, str]:
        """
        根据视频分析完成情况更新组状态。
        
        参数:
            group_id: 组ID
            
        返回:
            元组 (是否更新, 新状态)
        """
        from ..models import ResumeGroup
        
        try:
            group = ResumeGroup.objects.get(id=group_id)
        except ResumeGroup.DoesNotExist:
            return False, ""
        
        resumes = group.resumes.all()
        
        if not resumes.exists():
            return False, group.status
        
        # 检查所有简历是否已完成视频分析
        all_have_video = all(r.video_analysis is not None for r in resumes)
        all_video_completed = all(
            r.video_analysis and r.video_analysis.status == 'completed'
            for r in resumes
        )
        
        new_status = group.status
        
        if all_have_video and all_video_completed:
            if group.status in ['pending', 'interview_analysis']:
                new_status = 'interview_analysis_completed'
                group.status = new_status
                group.save()
                return True, new_status
        elif all_have_video and group.status == 'pending':
            new_status = 'interview_analysis'
            group.status = new_status
            group.save()
            return True, new_status
        
        return False, group.status
