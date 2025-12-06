"""
面试辅助API视图模块（精简版）。
"""
import logging
from datetime import datetime
from django.core.files.base import ContentFile
from django.http import JsonResponse

from apps.common.mixins import SafeAPIView
from apps.common.exceptions import ValidationException, NotFoundException

from .models import InterviewAssistSession
from services.agents import InterviewAssistAgent

logger = logging.getLogger(__name__)


class SessionView(SafeAPIView):
    """
    面试会话API
    POST: 创建会话
    GET: 获取会话详情
    DELETE: 结束会话
    """
    
    def handle_post(self, request):
        """创建面试会话。"""
        from apps.resume_screening.models import ResumeData
        
        resume_data_id = self.get_param(request, 'resume_data_id', required=True)
        job_config = self.get_param(request, 'job_config', default={})
        
        # 获取简历数据
        try:
            resume_data = ResumeData.objects.get(id=resume_data_id)
        except ResumeData.DoesNotExist:
            raise NotFoundException(f"简历数据不存在: {resume_data_id}")
        
        # 如果未提供则使用简历中的岗位信息
        if not job_config:
            job_config = {
                'title': resume_data.position_title,
                'description': '',
                'requirements': resume_data.position_details or {}
            }
        
        # 创建会话
        session = InterviewAssistSession.objects.create(
            resume_data=resume_data,
            job_config=job_config
        )
        
        # 构建简历摘要
        resume_summary = {
            'candidate_name': resume_data.candidate_name,
            'position_title': resume_data.position_title,
        }
        if resume_data.screening_score:
            resume_summary['screening_score'] = resume_data.screening_score
        if resume_data.screening_summary:
            resume_summary['screening_summary'] = resume_data.screening_summary[:200]
        
        return JsonResponse({
            'status': 'success',
            'message': '面试辅助会话已创建',
            'data': {
                'session_id': str(session.id),
                'candidate_name': resume_data.candidate_name,
                'position_title': job_config.get('title', resume_data.position_title),
                'created_at': session.created_at.isoformat(),
                'resume_summary': resume_summary
            }
        }, status=201)
    
    def handle_get(self, request, session_id=None):
        """获取会话详情。"""
        if not session_id:
            raise ValidationException("缺少会话ID")
        
        session = self.get_object_or_404(InterviewAssistSession, id=session_id)
        
        response_data = {
            'session_id': str(session.id),
            'candidate_name': session.resume_data.candidate_name,
            'position_title': session.job_config.get('title', ''),
            'current_round': session.current_round,
            'qa_count': len(session.qa_records) if session.qa_records else 0,
            'is_completed': session.is_completed,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat()
        }
        
        if session.is_completed and session.final_report:
            response_data['has_final_report'] = True
            response_data['final_report_summary'] = session.final_report.get(
                'overall_assessment', {}
            ).get('summary', '')
        
        return JsonResponse({
            'status': 'success',
            'data': response_data
        })
    
    def handle_delete(self, request, session_id=None):
        """删除会话。"""
        if not session_id:
            raise ValidationException("缺少会话ID")
        
        session = self.get_object_or_404(InterviewAssistSession, id=session_id)
        session.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': '会话已删除'
        })


class GenerateQuestionsView(SafeAPIView):
    """
    生成问题API
    POST: 生成候选问题（临时生成，不保存到数据库）
    """
    
    def handle_post(self, request, session_id):
        """生成候选问题。"""
        session = self.get_object_or_404(InterviewAssistSession, id=session_id)
        
        if session.is_completed:
            raise ValidationException("会话已结束，无法生成问题")
        
        categories = self.get_param(request, 'categories', default=['简历相关', '专业能力', '行为面试'])
        candidate_level = self.get_param(request, 'candidate_level', default='senior')
        count_per_category = self.get_int_param(request, 'count_per_category', default=2)
        focus_on_resume = self.get_param(request, 'focus_on_resume', default=True)
        interest_point_count = self.get_int_param(request, 'interest_point_count', default=2)
        
        # 限制兴趣点数量在 1-3 之间
        interest_point_count = max(1, min(3, interest_point_count))
        
        assistant = InterviewAssistAgent(job_config=session.job_config)
        
        all_questions = []
        interest_points = []
        
        # 生成基于简历的问题和兴趣点
        if focus_on_resume and session.resume_data.resume_content:
            result = assistant.generate_resume_based_questions(
                resume_content=session.resume_data.resume_content,
                count=count_per_category,
                interest_point_count=interest_point_count
            )
            all_questions.extend(result.get('questions', []))
            interest_points = result.get('interest_points', [])
        
        # 生成基于技能的问题
        for category in categories:
            if category != '简历相关':
                questions = assistant.generate_skill_based_questions(
                    category=category,
                    candidate_level=candidate_level,
                    count=count_per_category
                )
                all_questions.extend(questions)
        
        # 不保存到数据库，直接返回
        # 提取 resume_highlights（兼容旧格式）
        resume_highlights = [p.get('content', '') if isinstance(p, dict) else str(p) for p in interest_points]
        
        return JsonResponse({
            'status': 'success',
            'message': f'已生成{len(all_questions)}个候选问题',
            'data': {
                'session_id': str(session.id),
                'question_pool': all_questions,
                'resume_highlights': resume_highlights,
                'interest_points': interest_points  # 新格式：包含 content 和 question
            }
        })


class RecordQAView(SafeAPIView):
    """
    记录问答API
    POST: 记录问答并获取评估
    """
    
    def handle_post(self, request, session_id):
        """记录问答并生成候选提问。"""
        session = self.get_object_or_404(InterviewAssistSession, id=session_id)
        
        if session.is_completed:
            raise ValidationException("会话已结束")
        
        question_data = self.get_param(request, 'question', default={})
        answer_data = self.get_param(request, 'answer', default={})
        skip_evaluation = self.get_param(request, 'skip_evaluation', default=True)  # 默认跳过评估
        followup_count = self.get_int_param(request, 'followup_count', default=2)  # 追问问题数量
        alternative_count = self.get_int_param(request, 'alternative_count', default=3)  # 候选问题数量
        
        if not question_data.get('content') or not answer_data.get('content'):
            raise ValidationException("缺少问题或回答内容")
        
        assistant = InterviewAssistAgent(job_config=session.job_config)
        
        # 获取简历摘要
        resume_summary = ""
        if session.resume_data:
            resume_summary = f"""候选人: {session.resume_data.candidate_name}
应聘岗位: {session.resume_data.position_title}
简历内容摘要: {session.resume_data.resume_content[:1000] if session.resume_data.resume_content else '无'}"""
        
        # 获取历史对话记录
        conversation_history = session.qa_records or []
        
        # 可选：评估回答
        evaluation = None
        if not skip_evaluation:
            evaluation = assistant.evaluate_answer(
                question=question_data['content'],
                answer=answer_data['content'],
                target_skills=question_data.get('expected_skills', []),
                difficulty=question_data.get('difficulty', 5)
            )
        
        # 核心：生成候选提问（基于上下文、简历、岗位要求）
        candidate_questions = assistant.generate_candidate_questions(
            current_question=question_data['content'],
            current_answer=answer_data['content'],
            conversation_history=conversation_history,
            resume_summary=resume_summary,
            followup_count=followup_count,
            alternative_count=alternative_count
        )
        
        # 添加问答记录到会话（使用 JSON 存储）
        session.add_qa_record(
            question=question_data['content'],
            answer=answer_data['content'],
            evaluation=evaluation  # 可能为 None
        )
        session.save()
        
        round_number = session.current_round
        
        # 生成HR提示
        hr_hints = []
        if evaluation:
            hr_hints = self._generate_hr_hints(evaluation)
        else:
            hr_hints = ["请根据候选问题继续提问"]
        
        return JsonResponse({
            'status': 'success',
            'message': '问答已记录，候选问题已生成',
            'data': {
                'round_number': round_number,
                'evaluation': evaluation,  # 可能为 None
                'candidate_questions': candidate_questions,  # 新增：LLM生成的候选问题
                'hr_action_hints': hr_hints
            }
        })
    
    def _generate_hr_hints(self, evaluation: dict) -> list:
        """生成HR行动提示。"""
        hints = []
        score = evaluation.get('normalized_score', 50)
        confidence = evaluation.get('confidence_level', 'uncertain')
        should_followup = evaluation.get('should_followup', False)
        
        if should_followup:
            hints.append("建议追问具体细节以验证真实能力")
        
        if confidence == 'overconfident':
            hints.append("候选人可能存在夸大，建议深入追问")
        elif confidence == 'uncertain':
            hints.append("候选人表现不够确定，可考虑追问或跳过")
        
        if score < 50:
            hints.append("该回答得分较低，可考虑记录问题点")
        elif score >= 80:
            hints.append("回答质量较好，可继续下一问题")
        
        if not hints:
            hints.append("可选择追问或继续下一问题")
        
        return hints


class GenerateReportView(SafeAPIView):
    """
    生成报告API
    POST: 生成最终报告
    """
    
    def handle_post(self, request, session_id):
        """生成最终报告。"""
        session = self.get_object_or_404(InterviewAssistSession, id=session_id)
        
        include_conversation_log = self.get_param(request, 'include_conversation_log', default=True)
        hr_notes = self.get_param(request, 'hr_notes', default='')
        
        qa_records = session.qa_records or []
        
        if not qa_records:
            raise ValidationException("没有问答记录，无法生成报告")
        
        assistant = InterviewAssistAgent(job_config=session.job_config)
        
        # 生成报告
        report = assistant.generate_final_report(
            candidate_name=session.resume_data.candidate_name,
            qa_records=qa_records,
            hr_notes=hr_notes
        )
        
        # 保存报告
        session.final_report = report
        
        # 生成报告文件
        report_content = self._format_report(session, report, qa_records if include_conversation_log else None)
        filename = f"面试辅助报告_{session.resume_data.candidate_name}_{session.id}.md"
        session.report_file.save(filename, ContentFile(report_content.encode('utf-8')))
        
        session.save()
        
        return JsonResponse({
            'status': 'success',
            'message': '评估报告生成成功',
            'data': {
                'report': report,
                'report_file_url': session.report_file.url if session.report_file else None
            }
        })
    
    def _format_report(self, session, report: dict, qa_data: list = None) -> str:
        """将报告格式化为Markdown。"""
        lines = []
        lines.append("# 面试辅助评估报告\n")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"**候选人**: {session.resume_data.candidate_name}\n")
        lines.append(f"**应聘职位**: {session.job_config.get('title', '')}\n")
        lines.append("\n---\n")
        
        # 整体评估
        overall = report.get('overall_assessment', {})
        lines.append("## 整体评估\n")
        lines.append(f"- **推荐分数**: {overall.get('recommendation_score', 0)}/100\n")
        lines.append(f"- **推荐结论**: {overall.get('recommendation', '待定')}\n")
        lines.append(f"- **评估总结**: {overall.get('summary', '')}\n\n")
        
        # 问答记录
        if qa_data:
            lines.append("---\n## 问答记录\n")
            for qa in qa_data:
                lines.append(f"\n### 第{qa.get('round', 0)}轮\n")
                lines.append(f"**问题**: {qa.get('question', '')}\n\n")
                lines.append(f"**回答**: {qa.get('answer', '')}\n\n")
                if qa.get('evaluation'):
                    lines.append(f"**评分**: {qa['evaluation'].get('normalized_score', 0):.1f}/100\n")
        
        return "".join(lines)
