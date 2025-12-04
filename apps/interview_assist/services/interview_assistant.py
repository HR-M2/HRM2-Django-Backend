"""
面试助手服务模块。
"""
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class InterviewAssistant:
    """AI驱动的面试助手服务类。"""
    
    def __init__(
        self,
        llm_client=None,
        job_config: Dict = None,
        company_config: Dict = None
    ):
        self.llm_client = llm_client
        self.job_config = job_config or {}
        self.company_config = company_config or {}
    
    def generate_resume_based_questions(
        self,
        resume_content: str,
        count: int = 3
    ) -> Dict[str, Any]:
        """
        根据简历内容生成问题。
        
        参数:
            resume_content: 简历文本内容
            count: 要生成的问题数量
            
        返回:
            包含问题和兴趣点的字典
        """
        # 模拟实现 - 生产环境应使用LLM
        questions = [
            {
                "question": "请详细介绍一下您最具挑战性的项目经历",
                "category": "简历相关",
                "difficulty": 6,
                "expected_skills": ["项目经验", "问题解决"],
                "source": "resume_based"
            },
            {
                "question": "您在简历中提到的技术栈，能否举例说明实际应用场景？",
                "category": "简历相关",
                "difficulty": 5,
                "expected_skills": ["技术能力"],
                "source": "resume_based"
            },
            {
                "question": "您是如何处理项目中遇到的技术难题的？",
                "category": "简历相关",
                "difficulty": 7,
                "expected_skills": ["问题解决", "学习能力"],
                "source": "resume_based"
            }
        ]
        
        interest_points = [
            "项目经验丰富",
            "技术栈匹配度高",
            "有团队协作经验"
        ]
        
        return {
            "questions": questions[:count],
            "interest_points": interest_points
        }
    
    def generate_skill_based_questions(
        self,
        category: str,
        candidate_level: str = "senior",
        count: int = 2
    ) -> List[Dict]:
        """
        根据技能类别生成问题。
        
        参数:
            category: 问题类别
            candidate_level: 候选人经验级别
            count: 问题数量
            
        返回:
            问题字典列表
        """
        question_bank = {
            "专业能力": [
                {
                    "question": "请描述您对系统架构设计的理解",
                    "difficulty": 7,
                    "expected_skills": ["架构设计"]
                },
                {
                    "question": "您如何保证代码质量？",
                    "difficulty": 5,
                    "expected_skills": ["代码质量"]
                }
            ],
            "行为面试": [
                {
                    "question": "请描述一次您与团队成员意见不合的情况",
                    "difficulty": 6,
                    "expected_skills": ["沟通能力", "团队协作"]
                },
                {
                    "question": "您如何应对紧急的项目deadline？",
                    "difficulty": 5,
                    "expected_skills": ["压力管理"]
                }
            ]
        }
        
        questions = question_bank.get(category, [])
        for q in questions:
            q["category"] = category
            q["source"] = "skill_based"
        
        return questions[:count]
    
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        target_skills: List[str] = None,
        difficulty: int = 5
    ) -> Dict[str, Any]:
        """
        评估候选人的回答。
        
        参数:
            question: 面试问题
            answer: 候选人的回答
            target_skills: 要评估的目标技能
            difficulty: 问题难度
            
        返回:
            评估结果
        """
        # 模拟实现
        import random
        
        score = random.randint(50, 90)
        
        evaluation = {
            "normalized_score": score,
            "dimension_scores": {
                "relevance": random.randint(3, 5),
                "depth": random.randint(2, 5),
                "clarity": random.randint(3, 5),
                "examples": random.randint(2, 5)
            },
            "confidence_level": "confident" if score > 70 else "uncertain",
            "should_followup": score < 70,
            "followup_reason": "回答不够详细" if score < 70 else "",
            "feedback": self._generate_feedback(score)
        }
        
        return evaluation
    
    def _generate_feedback(self, score: int) -> str:
        """根据分数生成反馈。"""
        if score >= 80:
            return "回答全面且有深度，展示了扎实的专业能力"
        elif score >= 60:
            return "回答基本到位，但可以更加具体"
        else:
            return "回答较为简单，建议深入追问"
    
    def generate_followup_suggestions(
        self,
        original_question: str,
        answer: str,
        evaluation: Dict,
        target_skill: str = None
    ) -> Dict[str, Any]:
        """
        生成追问问题建议。
        
        参数:
            original_question: 原始问题
            answer: 候选人的回答
            evaluation: 回答评估
            target_skill: 要关注的技能
            
        返回:
            追问建议
        """
        suggestions = [
            {
                "question": "能否举一个具体的例子？",
                "purpose": "验证经验真实性",
                "difficulty": 6
            },
            {
                "question": "您在这个过程中遇到的最大挑战是什么？",
                "purpose": "深入了解问题解决能力",
                "difficulty": 7
            }
        ]
        
        return {
            "followup_suggestions": suggestions,
            "hr_hint": "建议追问具体细节以验证回答的真实性"
        }
    
    def generate_final_report(
        self,
        candidate_name: str,
        interviewer_name: str,
        qa_records: List[Dict],
        hr_notes: str = ""
    ) -> Dict[str, Any]:
        """
        生成最终面试报告。
        
        参数:
            candidate_name: 候选人姓名
            interviewer_name: 面试官姓名
            qa_records: QA记录列表
            hr_notes: HR备注
            
        返回:
            最终报告数据
        """
        # 计算平均分
        scores = [
            qa.get('evaluation', {}).get('normalized_score', 50)
            for qa in qa_records
        ]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # 确定推荐意见
        if avg_score >= 75:
            recommendation = "强烈推荐"
        elif avg_score >= 60:
            recommendation = "推荐"
        elif avg_score >= 45:
            recommendation = "待定"
        else:
            recommendation = "不推荐"
        
        report = {
            "overall_assessment": {
                "recommendation_score": round(avg_score, 1),
                "recommendation": recommendation,
                "summary": f"候选人{candidate_name}在面试中表现{'良好' if avg_score >= 60 else '一般'}。"
            },
            "dimension_analysis": {
                "专业能力": {"score": 4, "comment": "技术基础扎实"},
                "沟通能力": {"score": 3, "comment": "表达清晰"},
                "学习能力": {"score": 4, "comment": "学习态度积极"}
            },
            "skill_assessment": [
                {"skill": "技术能力", "level": "中高级", "evidence": "项目经验丰富"}
            ],
            "highlights": ["项目经验丰富", "沟通能力强"],
            "red_flags": [],
            "suggested_next_steps": ["安排二面", "与技术主管沟通"]
        }
        
        return report
