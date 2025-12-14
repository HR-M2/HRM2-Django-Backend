"""
面试辅助服务层模块。

数据库简化重构 - Phase 7:
- 创建会话时更新 Resume 状态为 INTERVIEWING
- 提供统一的面试会话操作接口
"""
import logging
from typing import Dict, List, Optional
from django.db import transaction

from apps.common.exceptions import ValidationException, NotFoundException

logger = logging.getLogger(__name__)


class InterviewSessionService:
    """面试会话服务类。"""
    
    @classmethod
    def get_session_by_id(cls, session_id: str):
        """
        根据ID获取面试会话。
        
        参数:
            session_id: 会话UUID
            
        返回:
            InterviewSession实例
            
        异常:
            NotFoundException: 如果会话不存在
        """
        from .models import InterviewSession
        
        try:
            return InterviewSession.objects.select_related('resume', 'resume__position').get(id=session_id)
        except InterviewSession.DoesNotExist:
            raise NotFoundException(f"面试会话不存在: {session_id}")
    
    @classmethod
    @transaction.atomic
    def create_session(cls, resume_id: str) -> 'InterviewSession':
        """
        创建面试会话并更新简历状态。
        
        参数:
            resume_id: 简历UUID
            
        返回:
            新创建的 InterviewSession 实例
            
        异常:
            NotFoundException: 如果简历不存在
        """
        from .models import InterviewSession
        from apps.resume.models import Resume
        from apps.resume.services import ResumeStatusTransition
        
        # 获取简历
        try:
            resume = Resume.objects.select_related('position').get(id=resume_id)
        except Resume.DoesNotExist:
            raise NotFoundException(f"简历不存在: {resume_id}")
        
        # 创建会话
        session = InterviewSession.objects.create(resume=resume)
        
        # 更新简历状态为面试中
        ResumeStatusTransition.transition_to_interviewing(str(resume.id))
        
        logger.info(f"创建面试会话: {session.id}，简历: {resume.candidate_name}")
        return session
    
    @classmethod
    def get_sessions_by_resume(cls, resume_id: str) -> List:
        """
        获取指定简历的所有面试会话。
        
        参数:
            resume_id: 简历UUID
            
        返回:
            InterviewSession 列表
        """
        from .models import InterviewSession
        
        return list(InterviewSession.objects.filter(
            resume_id=resume_id
        ).order_by('-created_at'))
    
    @classmethod
    @transaction.atomic
    def add_qa_record(
        cls,
        session_id: str,
        question: str,
        answer: str,
        evaluation: Dict = None
    ) -> 'InterviewSession':
        """
        添加问答记录到会话。
        
        参数:
            session_id: 会话UUID
            question: 问题内容
            answer: 回答内容
            evaluation: 评估结果（可选）
            
        返回:
            更新后的 InterviewSession 实例
        """
        session = cls.get_session_by_id(session_id)
        
        qa_records = session.qa_records or []
        qa_records.append({
            'round': len(qa_records) + 1,
            'question': question,
            'answer': answer,
            'evaluation': evaluation
        })
        session.qa_records = qa_records
        session.save(update_fields=['qa_records', 'updated_at'])
        
        logger.debug(f"添加问答记录到会话 {session_id}，当前轮次: {len(qa_records)}")
        return session
    
    @classmethod
    @transaction.atomic
    def set_final_report(cls, session_id: str, report: Dict) -> 'InterviewSession':
        """
        设置最终报告。
        
        参数:
            session_id: 会话UUID
            report: 报告内容
            
        返回:
            更新后的 InterviewSession 实例
        """
        session = cls.get_session_by_id(session_id)
        
        session.final_report = report
        session.save(update_fields=['final_report', 'updated_at'])
        
        logger.info(f"面试会话 {session_id} 报告已生成")
        return session
    
    @classmethod
    def get_job_config(cls, session_id: str) -> Dict:
        """
        获取会话关联的岗位配置。
        
        参数:
            session_id: 会话UUID
            
        返回:
            岗位配置字典
        """
        session = cls.get_session_by_id(session_id)
        resume = session.resume
        
        if resume and resume.position:
            return {
                'title': resume.position.title,
                'description': resume.position.description,
                'requirements': resume.position.requirements or {}
            }
        return {}
    
    @classmethod
    def delete_session(cls, session_id: str):
        """
        删除面试会话。
        
        参数:
            session_id: 会话UUID
        """
        session = cls.get_session_by_id(session_id)
        session.delete()
        logger.info(f"面试会话 {session_id} 已删除")
