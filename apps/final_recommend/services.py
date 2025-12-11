"""
最终推荐服务层模块。
"""
import logging
import json
from typing import Dict, List, Any, Tuple, Callable

# 注意: EvaluationAgentManager 已废弃并删除，批量评估功能不再支持
# 请使用 CandidateComprehensiveAnalyzer 进行单人综合分析

logger = logging.getLogger(__name__)


class EvaluationService:
    """面试后评估服务类。"""
    
    @classmethod
    def load_recruitment_criteria(cls, criteria_file: str = None) -> Dict[str, Any]:
        """从文件加载招聘标准或使用默认值。"""
        import os
        
        if criteria_file and os.path.exists(criteria_file):
            try:
                with open(criteria_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load criteria: {e}")
        
        # 默认标准
        return {
            "position": "Python开发工程师",
            "required_skills": ["Python", "Django", "MySQL", "Linux"],
            "optional_skills": ["Redis", "Docker", "Vue.js"],
            "min_experience": 2,
            "education": ["本科", "硕士"],
            "salary_range": [8000, 20000],
            "project_requirements": {
                "min_projects": 2,
                "team_lead_experience": True
            }
        }
    
    @classmethod
    def load_candidates_data(cls, group_id: str) -> Dict[str, Any]:
        """加载简历组的候选人数据。"""
        from apps.resume_screening.models import ResumeGroup, ResumeData
        
        try:
            group = ResumeGroup.objects.get(id=group_id)
            resumes = ResumeData.objects.filter(group=group)
            
            candidates = {}
            for resume in resumes:
                candidates[resume.candidate_name] = {
                    "resume_content": resume.resume_content,
                    "screening_score": resume.screening_score or {},
                    "screening_summary": resume.screening_summary or "",
                    "final_recommendation": {
                        "reasons": resume.json_report_content or resume.screening_summary or ""
                    }
                }
            
            return candidates
        except ResumeGroup.DoesNotExist:
            logger.error(f"Resume group not found: {group_id}")
            return {}
    
    @classmethod
    def load_personality_data(cls, group_id: str) -> Tuple[Dict, Dict]:
        """加载候选人的人格和欺诈检测数据。"""
        from apps.resume_screening.models import ResumeGroup, ResumeData
        
        big_five_scores = {}
        fraud_scores = {}
        
        try:
            group = ResumeGroup.objects.get(id=group_id)
            resumes = ResumeData.objects.filter(group=group)
            
            for resume in resumes:
                name = resume.candidate_name
                
                if resume.video_analysis:
                    va = resume.video_analysis
                    big_five_scores[name] = {
                        'openness': va.openness_score or 'N/A',
                        'conscientiousness': va.conscientiousness_score or 'N/A',
                        'extraversion': va.extraversion_score or 'N/A',
                        'agreeableness': va.agreeableness_score or 'N/A',
                        'neuroticism': va.neuroticism_score or 'N/A'
                    }
                    fraud_scores[name] = va.fraud_score or 'N/A'
                else:
                    big_five_scores[name] = {
                        'openness': 'N/A',
                        'conscientiousness': 'N/A',
                        'extraversion': 'N/A',
                        'agreeableness': 'N/A',
                        'neuroticism': 'N/A'
                    }
                    fraud_scores[name] = 'N/A'
        
        except ResumeGroup.DoesNotExist:
            logger.error(f"Resume group not found: {group_id}")
        
        return big_five_scores, fraud_scores
    
    @classmethod
    def generate_candidate_info(
        cls,
        candidates_data: Dict,
        big_five_scores: Dict,
        fraud_scores: Dict
    ) -> str:
        """生成格式化的候选人信息字符串。"""
        infos = []
        
        for name, data in candidates_data.items():
            reasons = data.get("final_recommendation", {}).get("reasons", "")
            big_five = big_five_scores.get(name, {})
            fraud = fraud_scores.get(name, 'N/A')
            
            info = f"""
候选人：{name}
简历信息：{reasons[:500] if reasons else '暂无详细信息'}

大五人格测试结果：
- 开放性: {big_five.get('openness', 'N/A')}
- 尽责性: {big_five.get('conscientiousness', 'N/A')}
- 外倾性: {big_five.get('extraversion', 'N/A')}
- 宜人性: {big_five.get('agreeableness', 'N/A')}
- 神经质: {big_five.get('neuroticism', 'N/A')}

欺诈检测得分: {fraud}（0.6以下为安全范围）
{"=" * 50}
"""
            infos.append(info)
        
        return "\n".join(infos)
    
    # run_evaluation 方法已废弃并删除
    # 批量评估功能不再支持，请使用 CandidateComprehensiveAnalyzer 进行单人综合分析
    # 参见: apps/final_recommend/views.py 中的 CandidateComprehensiveAnalysisView
