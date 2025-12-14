"""
最终推荐服务层模块。

数据库简化重构 - Phase 7:
- 分析完成时更新 Resume 状态为 ANALYZED
- 使用新的 ComprehensiveAnalysis 模型
- 从 Resume 获取筛选结果
"""
import logging
import json
from typing import Dict, List, Any, Callable

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


class ComprehensiveAnalysisService:
    """综合分析服务类。"""
    
    @classmethod
    def get_analysis_by_id(cls, analysis_id: str):
        """
        根据ID获取综合分析记录。
        
        参数:
            analysis_id: 分析记录UUID
            
        返回:
            ComprehensiveAnalysis实例
        """
        from .models import ComprehensiveAnalysis
        from apps.common.exceptions import NotFoundException
        
        try:
            return ComprehensiveAnalysis.objects.select_related('resume', 'resume__position').get(id=analysis_id)
        except ComprehensiveAnalysis.DoesNotExist:
            raise NotFoundException(f"综合分析记录不存在: {analysis_id}")
    
    @classmethod
    def get_latest_by_resume(cls, resume_id: str):
        """
        获取指定简历的最新分析记录。
        
        参数:
            resume_id: 简历UUID
            
        返回:
            ComprehensiveAnalysis实例或None
        """
        from .models import ComprehensiveAnalysis
        
        return ComprehensiveAnalysis.objects.filter(
            resume_id=resume_id
        ).order_by('-created_at').first()
    
    @classmethod
    def create_analysis(
        cls,
        resume_id: str,
        final_score: float,
        recommendation: Dict,
        dimension_scores: Dict,
        report: str = ''
    ):
        """
        创建综合分析记录并更新简历状态。
        
        参数:
            resume_id: 简历UUID
            final_score: 最终评分
            recommendation: 推荐结果字典
            dimension_scores: 维度评分字典
            report: 综合报告内容
            
        返回:
            新创建的 ComprehensiveAnalysis 实例
        """
        from django.db import transaction
        from .models import ComprehensiveAnalysis
        from apps.resume.models import Resume
        from apps.resume.services import ResumeStatusTransition
        from apps.common.exceptions import NotFoundException
        
        # 获取简历
        try:
            resume = Resume.objects.get(id=resume_id)
        except Resume.DoesNotExist:
            raise NotFoundException(f"简历不存在: {resume_id}")
        
        with transaction.atomic():
            # 创建分析记录
            analysis = ComprehensiveAnalysis.objects.create(
                resume=resume,
                final_score=final_score,
                recommendation=recommendation,
                dimension_scores=dimension_scores,
                report=report
            )
            
            # 更新简历状态为已分析
            ResumeStatusTransition.transition_to_analyzed(str(resume.id))
            
            logger.info(f"创建综合分析记录: {analysis.id}，候选人: {resume.candidate_name}")
            return analysis
    
    @classmethod
    def get_statistics(cls) -> Dict:
        """
        获取综合分析统计数据。
        
        返回:
            统计数据字典
        """
        from .models import ComprehensiveAnalysis
        
        # 统计已完成综合分析的唯一简历数量
        analyzed_count = ComprehensiveAnalysis.objects.values(
            'resume_id'
        ).distinct().count()
        
        return {
            'analyzed_count': analyzed_count
        }
