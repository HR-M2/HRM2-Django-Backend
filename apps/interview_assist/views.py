"""
面试辅助API视图模块 - 与原版 RecruitmentSystemAPI 返回格式保持一致。
"""
import logging
from datetime import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
from django.http import JsonResponse
from rest_framework import status

from apps.common.mixins import SafeAPIView
from apps.common.response import APIResponse
from apps.common.exceptions import ValidationException, NotFoundException

from .models import InterviewAssistSession, InterviewQARecord
from .services import InterviewAssistant

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
        interviewer_name = self.get_param(request, 'interviewer_name', default='面试官')
        job_config = self.get_param(request, 'job_config', default={})
        company_config = self.get_param(request, 'company_config', default={})
        
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
            interviewer_name=interviewer_name,
            job_config=job_config,
            company_config=company_config,
            status='active'
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
        
        # 返回与原版一致的格式
        return JsonResponse({
            'status': 'success',
            'message': '面试辅助会话已创建',
            'data': {
                'session_id': str(session.id),
                'candidate_name': resume_data.candidate_name,
                'position_title': job_config.get('title', resume_data.position_title),
                'status': session.status,
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
            'interviewer_name': session.interviewer_name,
            'status': session.status,
            'current_round': session.current_round,
            'qa_count': session.qa_records.count(),
            'question_pool_count': len(session.question_pool),
            'resume_highlights': session.resume_highlights,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat()
        }
        
        if session.status == 'completed' and session.final_report:
            response_data['has_final_report'] = True
            response_data['final_report_summary'] = session.final_report.get(
                'overall_assessment', {}
            ).get('summary', '')
        
        # 返回与原版一致的格式
        return JsonResponse({
            'status': 'success',
            'data': response_data
        })
    
    def handle_delete(self, request, session_id=None):
        """结束会话。"""
        if not session_id:
            raise ValidationException("缺少会话ID")
        
        session = self.get_object_or_404(InterviewAssistSession, id=session_id)
        session.status = 'completed'
        session.save()
        
        # 返回与原版一致的格式
        return JsonResponse({
            'status': 'success',
            'message': '会话已结束'
        })


class GenerateQuestionsView(SafeAPIView):
    """
    生成问题API
    POST: 生成候选问题
    """
    
    def handle_post(self, request, session_id):
        """生成候选问题。"""
        session = self.get_object_or_404(InterviewAssistSession, id=session_id)
        
        if session.status != 'active':
            raise ValidationException("会话已结束，无法生成问题")
        
        categories = self.get_param(request, 'categories', default=['简历相关', '专业能力', '行为面试'])
        candidate_level = self.get_param(request, 'candidate_level', default='senior')
        count_per_category = self.get_int_param(request, 'count_per_category', default=2)
        focus_on_resume = self.get_param(request, 'focus_on_resume', default=True)
        
        assistant = InterviewAssistant(
            job_config=session.job_config,
            company_config=session.company_config
        )
        
        all_questions = []
        interest_points = []
        
        # 生成基于简历的问题
        if focus_on_resume and session.resume_data.resume_content:
            result = assistant.generate_resume_based_questions(
                resume_content=session.resume_data.resume_content,
                count=count_per_category
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
        
        # 保存到会话
        session.question_pool = all_questions
        session.resume_highlights = interest_points
        session.save()
        
        # 返回与原版一致的格式
        return JsonResponse({
            'status': 'success',
            'message': f'已生成{len(all_questions)}个候选问题',
            'data': {
                'session_id': str(session.id),
                'question_pool': all_questions,
                'resume_highlights': interest_points
            }
        })


class RecordQAView(SafeAPIView):
    """
    记录问答API
    POST: 记录问答并获取评估
    """
    
    def handle_post(self, request, session_id):
        """记录问答并获取评估。"""
        session = self.get_object_or_404(InterviewAssistSession, id=session_id)
        
        if session.status != 'active':
            raise ValidationException("会话已结束")
        
        question_data = self.get_param(request, 'question', default={})
        answer_data = self.get_param(request, 'answer', default={})
        
        if not question_data.get('content') or not answer_data.get('content'):
            raise ValidationException("缺少问题或回答内容")
        
        # 更新轮次
        session.current_round += 1
        round_number = session.current_round
        
        assistant = InterviewAssistant(
            job_config=session.job_config,
            company_config=session.company_config
        )
        
        # 评估回答
        evaluation = assistant.evaluate_answer(
            question=question_data['content'],
            answer=answer_data['content'],
            target_skills=question_data.get('expected_skills', []),
            difficulty=question_data.get('difficulty', 5)
        )
        
        # 生成追问建议
        followup_suggestions = []
        followup_recommendation = {
            'should_followup': evaluation.get('should_followup', False),
            'reason': evaluation.get('followup_reason', ''),
            'suggested_followups': []
        }
        
        if evaluation.get('should_followup'):
            result = assistant.generate_followup_suggestions(
                original_question=question_data['content'],
                answer=answer_data['content'],
                evaluation=evaluation,
                target_skill=question_data.get('expected_skills', [''])[0] if question_data.get('expected_skills') else None
            )
            followup_suggestions = result.get('followup_suggestions', [])
            followup_recommendation['suggested_followups'] = followup_suggestions
            followup_recommendation['hr_hint'] = result.get('hr_hint', '')
        
        # 创建QA记录
        qa_record = InterviewQARecord.objects.create(
            session=session,
            round_number=round_number,
            question=question_data['content'],
            question_source=question_data.get('source', 'hr_custom'),
            question_category=question_data.get('category', ''),
            expected_skills=question_data.get('expected_skills', []),
            question_difficulty=question_data.get('difficulty', 5),
            related_interest_point=question_data.get('interest_point'),
            answer=answer_data['content'],
            answer_recorded_at=timezone.now(),
            answer_duration_seconds=answer_data.get('duration_seconds'),
            evaluation=evaluation,
            followup_suggestions=followup_suggestions
        )
        
        session.save()
        
        # 生成HR提示
        hr_hints = self._generate_hr_hints(evaluation)
        
        # 返回与原版一致的格式
        return JsonResponse({
            'status': 'success',
            'message': '问答已记录，评估完成',
            'data': {
                'round_number': round_number,
                'qa_record_id': str(qa_record.id),
                'evaluation': evaluation,
                'followup_recommendation': followup_recommendation,
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
        
        qa_records = session.qa_records.all().order_by('round_number')
        
        if not qa_records.exists():
            raise ValidationException("没有问答记录，无法生成报告")
        
        # 准备QA数据
        qa_data = [
            {
                'round_number': r.round_number,
                'question': r.question,
                'answer': r.answer,
                'evaluation': r.evaluation,
                'was_followed_up': r.was_followed_up
            }
            for r in qa_records
        ]
        
        assistant = InterviewAssistant(
            job_config=session.job_config,
            company_config=session.company_config
        )
        
        # 生成报告
        report = assistant.generate_final_report(
            candidate_name=session.resume_data.candidate_name,
            interviewer_name=session.interviewer_name,
            qa_records=qa_data,
            hr_notes=hr_notes
        )
        
        # 保存报告
        session.final_report = report
        session.status = 'completed'
        
        # 生成报告文件
        report_content = self._format_report(session, report, qa_data if include_conversation_log else None)
        filename = f"面试辅助报告_{session.resume_data.candidate_name}_{session.id}.md"
        session.report_file.save(filename, ContentFile(report_content.encode('utf-8')))
        
        session.save()
        
        # 返回与原版一致的格式
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
        lines.append(f"**面试官**: {session.interviewer_name}\n")
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
                lines.append(f"\n### 第{qa['round_number']}轮\n")
                lines.append(f"**问题**: {qa['question']}\n\n")
                lines.append(f"**回答**: {qa['answer']}\n\n")
                if qa.get('evaluation'):
                    lines.append(f"**评分**: {qa['evaluation'].get('normalized_score', 0):.1f}/100\n")
        
        return "".join(lines)
