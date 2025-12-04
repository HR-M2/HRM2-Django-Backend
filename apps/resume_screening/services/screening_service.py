"""
简历筛选服务层模块。
"""
import os
import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from django.conf import settings

from apps.common.utils import generate_hash, extract_name_from_filename
from apps.common.exceptions import ValidationException, ServiceException
from services.agents import ScreeningAgentManager

logger = logging.getLogger(__name__)


class ScreeningService:
    """简历筛选操作服务类。"""
    
    WEIGHTS = {"hr": 0.3, "technical": 0.4, "manager": 0.3}
    
    @classmethod
    def parse_input_data(cls, data: Dict) -> Tuple[Dict, List[Dict]]:
        """
        解析并验证来自前端的输入数据。
        
        参数:
            data: 包含岗位和简历的请求数据
            
        返回:
            元组 (position_data, resumes_list)
            
        异常:
            ValidationException: 如果数据格式无效
        """
        if not isinstance(data, dict):
            raise ValidationException("请求体必须为JSON对象")
        
        position = data.get("position")
        resumes = data.get("resumes")
        
        errors = {}
        if position is None:
            errors["position"] = "缺少position字段"
        elif not isinstance(position, dict):
            errors["position"] = "position必须为对象"
        
        if resumes is None:
            errors["resumes"] = "缺少resumes字段"
        elif not isinstance(resumes, list):
            errors["resumes"] = "resumes必须为列表"
        
        if errors:
            raise ValidationException("参数验证失败", errors)
        
        # 解析简历
        parsed_resumes = []
        for idx, item in enumerate(resumes):
            if not isinstance(item, dict):
                raise ValidationException(f"第{idx}份简历必须为对象")
            
            name = item.get("name") or item.get("filename") or f"resume_{idx}"
            content = item.get("content")
            metadata = item.get("metadata", {}) or {}
            
            if content is None:
                raise ValidationException(f"第{idx}份简历缺少content字段")
            
            parsed_resumes.append({
                "name": name,
                "content": content,
                "metadata": {
                    "size": metadata.get("size", 0),
                    "type": metadata.get("type", "text/plain")
                }
            })
        
        return position, parsed_resumes
    
    @classmethod
    def run_screening(
        cls,
        task,
        position_data: Dict,
        resumes_data: List[Dict],
        run_chat: bool = True
    ) -> Dict[str, str]:
        """
        为多份简历运行筛选流程。
        
        参数:
            task: ResumeScreeningTask实例
            position_data: 岗位/职位信息
            resumes_data: 简历数据列表
            run_chat: 是否运行实际的LLM对话
            
        返回:
            候选人名称到报告内容的映射字典
        """
        from .report_service import ReportService
        
        results = {}
        
        for idx, resume in enumerate(resumes_data):
            try:
                candidate_name = extract_name_from_filename(resume['name'])
                resume_text = resume['content']
                
                # 更新任务进度
                task.current_step = idx + 1
                task.progress = int((idx + 1) / len(resumes_data) * 50)  # 前50%用于处理
                task.save()
                
                if run_chat:
                    # 运行代理筛选
                    agent_manager = ScreeningAgentManager(position_data)
                    agent_manager.set_task(task)
                    agent_manager.setup()
                    messages = agent_manager.run_screening(candidate_name, resume_text)
                    
                    # 提取并保存结果
                    extracted = cls.extract_scores_and_comments(messages)
                    
                    # 生成并保存报告
                    md_content = ReportService.generate_md_report(
                        candidate_name, 
                        messages, 
                        extracted
                    )
                    json_content = ReportService.generate_json_report(
                        candidate_name,
                        extracted,
                        messages
                    )
                    
                    results[candidate_name] = {
                        'md_content': md_content,
                        'json_content': json_content,
                        'scores': extracted['scores'],
                        'summary': extracted['final_recommendation']['reasons'][:500]
                    }
                else:
                    # 测试用模拟结果
                    results[candidate_name] = {
                        'md_content': f"# {candidate_name} 简历初筛结果\n\n暂无评审结果",
                        'json_content': '{}',
                        'scores': {},
                        'summary': ''
                    }
                
            except Exception as e:
                logger.error(f"Error screening {resume.get('name')}: {e}")
                raise ServiceException(f"简历筛选失败: {str(e)}")
        
        return results
    
    @classmethod
    def extract_scores_and_comments(cls, conversation_history: List[Dict]) -> Dict:
        """
        从对话历史中提取分数、评论和推荐。
        
        参数:
            conversation_history: 消息字典列表
            
        返回:
            包含提取的分数和评论的字典
        """
        result = {
            "scores": {
                "hr_score": 0.0,
                "technical_score": 0.0,
                "manager_score": 0.0,
                "comprehensive_score": 0.0
            },
            "salary_suggestions": {
                "hr_suggestion": "",
                "technical_suggestion": "",
                "manager_suggestion": "",
                "final_suggestion": ""
            },
            "review_comments": {
                "hr_comments": "",
                "technical_comments": "",
                "manager_comments": ""
            },
            "final_recommendation": {
                "decision": "",
                "reasons": ""
            }
        }
        
        for message in conversation_history:
            content = message.get('content', '')
            speaker = message.get('name', '')
            
            if speaker == "HR_Expert":
                cls._extract_hr_data(content, result)
            elif speaker == "Technical_Expert":
                cls._extract_technical_data(content, result)
            elif speaker == "Project_Manager_Expert":
                cls._extract_manager_data(content, result)
            elif speaker == "Critic":
                cls._extract_critic_data(content, result)
        
        # 如果未提供则计算综合分
        if result["scores"]["comprehensive_score"] == 0:
            scores = result["scores"]
            comprehensive = (
                scores["hr_score"] * cls.WEIGHTS["hr"] +
                scores["technical_score"] * cls.WEIGHTS["technical"] +
                scores["manager_score"] * cls.WEIGHTS["manager"]
            )
            result["scores"]["comprehensive_score"] = round(comprehensive, 2)
        
        return result
    
    @classmethod
    def _extract_hr_data(cls, content: str, result: Dict):
        """从HR专家内容中提取数据。"""
        # 提取分数
        match = re.search(r'HR评分[：:]\s*\**([0-9.]+)\**分', content)
        if match:
            result["scores"]["hr_score"] = float(match.group(1))
        else:
            match = re.search(r'(?i)hr.*?评分[^\d]{0,10}([0-9.]+)分', content, re.DOTALL)
            if match:
                result["scores"]["hr_score"] = float(match.group(1))
        
        # 薪资建议
        match = re.search(r'建议月薪[：:]\s*\**([0-9\-~～]+)\**', content)
        if match:
            result["salary_suggestions"]["hr_suggestion"] = match.group(1)
        
        # 评论
        comment = re.sub(r'HR评分[：:]\s*\**[0-9.]+\**分.*?理由[：:]\s*', '', content, flags=re.DOTALL)
        comment = re.sub(r'建议月薪[：:]\s*\**[0-9\-~～]+\**.*', '', comment, flags=re.DOTALL)
        result["review_comments"]["hr_comments"] = comment.strip()
    
    @classmethod
    def _extract_technical_data(cls, content: str, result: Dict):
        """从技术专家内容中提取数据。"""
        match = re.search(r'技术评分[：:]\s*\**([0-9.]+)\**分', content)
        if match:
            result["scores"]["technical_score"] = float(match.group(1))
        else:
            match = re.search(r'(?i)技术.*?评分[^\d]{0,10}([0-9.]+)分', content, re.DOTALL)
            if match:
                result["scores"]["technical_score"] = float(match.group(1))
        
        match = re.search(r'建议月薪[：:]\s*\**([0-9\-~～]+)\**', content)
        if match:
            result["salary_suggestions"]["technical_suggestion"] = match.group(1)
        
        comment = re.sub(r'技术评分[：:]\s*\**[0-9.]+\**分.*?理由[：:]\s*', '', content, flags=re.DOTALL)
        comment = re.sub(r'建议月薪[：:]\s*\**[0-9\-~～]+\**.*', '', comment, flags=re.DOTALL)
        result["review_comments"]["technical_comments"] = comment.strip()
    
    @classmethod
    def _extract_manager_data(cls, content: str, result: Dict):
        """从管理专家内容中提取数据。"""
        match = re.search(r'管理评分[：:]\s*\**([0-9.]+)\**分', content)
        if match:
            result["scores"]["manager_score"] = float(match.group(1))
        else:
            match = re.search(r'(?i)管理.*?评分[^\d]{0,10}([0-9.]+)分', content, re.DOTALL)
            if match:
                result["scores"]["manager_score"] = float(match.group(1))
        
        match = re.search(r'建议月薪[：:]\s*\**([0-9\-~～]+)\**', content)
        if match:
            result["salary_suggestions"]["manager_suggestion"] = match.group(1)
        
        comment = re.sub(r'管理评分[：:]\s*\**[0-9.]+\**分.*?理由[：:]\s*', '', content, flags=re.DOTALL)
        comment = re.sub(r'建议月薪[：:]\s*\**[0-9\-~～]+\**.*', '', comment, flags=re.DOTALL)
        result["review_comments"]["manager_comments"] = comment.strip()
    
    @classmethod
    def _extract_critic_data(cls, content: str, result: Dict):
        """从评审员/最终审查内容中提取数据。"""
        # 综合分数
        match = re.search(r'综合评分[：:]\s*\**([0-9.]+)\**分', content)
        if match:
            result["scores"]["comprehensive_score"] = float(match.group(1))
        else:
            match = re.search(r'(?i)综合.*?评分[^\d]{0,10}([0-9.]+)分', content, re.DOTALL)
            if match:
                result["scores"]["comprehensive_score"] = float(match.group(1))
        
        # 最终薪资建议
        match = re.search(r'建议月薪[：:]\s*\**([0-9\-~～]+)\**', content)
        if match:
            result["salary_suggestions"]["final_suggestion"] = match.group(1)
        
        # 决策
        decision_patterns = [
            r'招聘建议[：:]\s*\**\s*(推荐面试|备选|不匹配|建议面试|通过|不通过)\s*\**',
            r'最终建议[：:]\s*\**\s*(推荐面试|备选|不匹配|建议面试|通过|不通过)\s*\**',
            r'决策[：:]\s*\**\s*(推荐面试|备选|不匹配|建议面试|通过|不通过)\s*\**'
        ]
        
        for pattern in decision_patterns:
            match = re.search(pattern, content)
            if match:
                result["final_recommendation"]["decision"] = match.group(1)
                break
        
        result["final_recommendation"]["reasons"] = content
