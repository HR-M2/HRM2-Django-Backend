"""
报告生成服务模块。

数据库简化重构 - Phase 7:
- 更新为使用新的 Resume 模型
- 删除对废弃模型 ScreeningReport, ResumeData 的引用
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile

from apps.common.utils import ensure_dir, sanitize_filename

logger = logging.getLogger(__name__)


class ReportService:
    """生成和管理筛选报告的服务类。"""
    
    @classmethod
    def generate_md_report(
        cls,
        candidate_name: str,
        conversation_history: List[Dict],
        extracted_data: Dict
    ) -> str:
        """
        从对话历史生成Markdown报告。
        
        参数:
            candidate_name: 候选人名称
            conversation_history: 对话消息列表
            extracted_data: 提取的分数和评论
            
        返回:
            Markdown内容字符串
        """
        lines = []
        
        # 标题
        lines.append(f"# {candidate_name} 简历初筛报告\n")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("\n---\n")
        
        # 分数汇总
        lines.append("## 评分汇总\n")
        scores = extracted_data.get('scores', {})
        lines.append("| 维度 | 评分 |\n")
        lines.append("|------|------|\n")
        lines.append(f"| HR评分 | {scores.get('hr_score', 0)} |\n")
        lines.append(f"| 技术评分 | {scores.get('technical_score', 0)} |\n")
        lines.append(f"| 管理评分 | {scores.get('manager_score', 0)} |\n")
        lines.append(f"| **综合评分** | **{scores.get('comprehensive_score', 0)}** |\n")
        lines.append("\n")
        
        # 薪资建议
        salary = extracted_data.get('salary_suggestions', {})
        if salary.get('final_suggestion'):
            lines.append(f"**建议月薪**: {salary.get('final_suggestion')}\n\n")
        
        # 最终推荐
        recommendation = extracted_data.get('final_recommendation', {})
        if recommendation.get('decision'):
            lines.append(f"**招聘建议**: {recommendation.get('decision')}\n\n")
        
        # 详细评审记录
        lines.append("## 详细评审记录\n")
        for message in conversation_history:
            speaker = message.get('name', 'Unknown')
            content = message.get('content', '')
            
            lines.append(f"### {speaker}\n\n")
            lines.append(f"{content}\n\n")
            lines.append("---\n\n")
        
        return "".join(lines)
    
    @classmethod
    def generate_json_report(
        cls,
        candidate_name: str,
        extracted_data: Dict,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        从提取的数据生成JSON报告。
        
        参数:
            candidate_name: 候选人名称
            extracted_data: 提取的分数和评论
            conversation_history: 可选的对话历史
            
        返回:
            JSON字符串
        """
        report_data = {
            "file_name": f"{candidate_name}简历初筛结果.md",
            "name": candidate_name,
            "generated_at": datetime.now().isoformat(),
            "scores": extracted_data.get("scores", {}),
            "salary_suggestions": extracted_data.get("salary_suggestions", {}),
            "review_comments": extracted_data.get("review_comments", {}),
            "final_recommendation": extracted_data.get("final_recommendation", {})
        }
        
        if conversation_history:
            report_data["conversation_history"] = conversation_history
        
        return json.dumps(report_data, ensure_ascii=False, indent=2)
    
    @classmethod
    def save_report_to_resume(
        cls,
        resume,
        result: Dict,
        md_content: str
    ):
        """
        将筛选报告保存到 Resume 模型。
        
        参数:
            resume: Resume 实例
            result: 筛选结果字典（包含 scores, summary 等）
            md_content: Markdown报告内容
            
        返回:
            更新后的 Resume 实例
        """
        from apps.resume.services import ResumeService
        
        return ResumeService.set_screening_result(
            resume_id=str(resume.id),
            result=result,
            report_md=md_content
        )
    
    @classmethod
    def save_or_update_resume(
        cls,
        task,
        position,
        candidate_name: str,
        resume_content: str,
        filename: str,
        screening_result: Dict = None
    ):
        """
        将简历数据保存到 Resume 模型，如果已存在则更新筛选结果。
        
        参数:
            task: ScreeningTask 实例
            position: Position 实例
            candidate_name: 候选人名称
            resume_content: 简历内容
            filename: 原始文件名
            screening_result: 包含分数和报告的筛选结果（可选）
            
        返回:
            tuple: (Resume实例, 是否为新创建)
        """
        from apps.resume.models import Resume
        from apps.resume.services import ResumeService
        from apps.common.utils import generate_hash
        
        # 生成哈希
        resume_hash = generate_hash(resume_content)
        
        # 检查是否已存在
        existing = Resume.objects.filter(file_hash=resume_hash).first()
        
        if existing:
            # 如果存在且有筛选结果，更新筛选结果
            if screening_result:
                existing.screening_result = {
                    'scores': screening_result.get('scores', {}),
                    'summary': screening_result.get('summary', ''),
                }
                existing.screening_report = screening_result.get('md_content', '')
                existing.status = Resume.Status.SCREENED
                existing.save(update_fields=['screening_result', 'screening_report', 'status', 'updated_at'])
                logger.info(f"更新现有简历（哈希: {resume_hash[:8]}...）的筛选结果")
            
            return existing, False
        
        # 创建新记录
        resume = Resume.objects.create(
            filename=filename,
            file_hash=resume_hash,
            file_size=len(resume_content.encode('utf-8')),
            file_type='text/plain',
            candidate_name=candidate_name,
            content=resume_content,
            position=position,
            status=Resume.Status.SCREENED if screening_result else Resume.Status.PENDING,
            screening_result={
                'scores': screening_result.get('scores', {}),
                'summary': screening_result.get('summary', ''),
            } if screening_result else None,
            screening_report=screening_result.get('md_content', '') if screening_result else None
        )
        
        logger.info(f"创建新简历: {resume.id} ({candidate_name})")
        return resume, True

    @classmethod
    def save_resume_data(
        cls,
        task,
        position,
        candidate_name: str,
        resume_content: str,
        filename: str,
        screening_result: Dict
    ):
        """
        将简历数据保存到 Resume 模型（兼容旧接口）。
        
        参数:
            task: ScreeningTask 实例
            position: Position 实例
            candidate_name: 候选人名称
            resume_content: 简历内容
            filename: 原始文件名
            screening_result: 包含分数和报告的筛选结果
            
        返回:
            tuple: (Resume实例, 是否为新创建)
        """
        return cls.save_or_update_resume(
            task=task,
            position=position,
            candidate_name=candidate_name,
            resume_content=resume_content,
            filename=filename,
            screening_result=screening_result
        )
