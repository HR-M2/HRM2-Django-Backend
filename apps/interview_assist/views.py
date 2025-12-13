"""
面试辅助API视图模块（精简版）。

数据库简化重构：
- 使用 InterviewSession 模型（原 InterviewAssistSession 已重命名）
- 关联到 Resume（原关联 ResumeData）
- job_config 从 resume.position 获取
"""
import logging
from datetime import datetime
from django.core.files.base import ContentFile

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import serializers

from apps.common.mixins import SafeAPIView
from apps.common.response import ApiResponse
from apps.common.exceptions import ValidationException, NotFoundException
from apps.common.schemas import (
    api_response, success_response,
    SessionItemSerializer, SessionCreateResponseSerializer, SessionDetailSerializer,
    GenerateQuestionsResponseSerializer, RecordQAResponseSerializer,
    InterviewReportResponseSerializer,
    SessionCreateRequestSerializer, GenerateQuestionsRequestSerializer,
    RecordQARequestSerializer, GenerateReportRequestSerializer,
)

from .models import InterviewSession
from apps.resume.models import Resume
from services.agents import InterviewAssistAgent

logger = logging.getLogger(__name__)


class SessionListView(SafeAPIView):
    """
    面试会话列表API
    GET: 获取会话列表（需要 resume_id 参数）
    POST: 创建会话
    """
    
    @extend_schema(
        summary="获取面试会话列表",
        description="获取指定简历的面试会话列表",
        parameters=[
            OpenApiParameter(name='resume_id', type=str, required=True, description='简历ID（必填）'),
        ],
        responses={200: api_response(SessionItemSerializer(many=True), "SessionList")},
        tags=["interviews"],
    )
    def handle_get(self, request):
        """获取会话列表。"""
        resume_id = request.GET.get('resume_id')
        if not resume_id:
            raise ValidationException("缺少简历ID参数")
        
        sessions = InterviewSession.objects.filter(
            resume_id=resume_id
        ).order_by('-created_at')
        
        data = []
        for session in sessions:
            session_data = {
                'id': str(session.id),
                'resume_id': str(session.resume_id),
                'qa_records': session.qa_records or [],
                'created_at': session.created_at.isoformat(),
            }
            if session.final_report:
                session_data['final_report'] = session.final_report
            data.append(session_data)
        
        return ApiResponse.success(data=data)
    
    @extend_schema(
        summary="创建面试会话",
        description="为指定简历创建新的面试辅助会话",
        request=SessionCreateRequestSerializer,
        responses={201: api_response(SessionCreateResponseSerializer(), "SessionCreate")},
        tags=["interviews"],
    )
    def handle_post(self, request):
        """创建面试会话。"""
        resume_id = self.get_param(request, 'resume_id') or self.get_param(request, 'resume_data_id', required=True)
        
        # 获取简历
        try:
            resume = Resume.objects.get(id=resume_id)
        except Resume.DoesNotExist:
            raise NotFoundException(f"简历不存在: {resume_id}")
        
        # 从 resume.position 获取岗位配置
        job_config = {}
        if resume.position:
            job_config = {
                'title': resume.position.title,
                'description': resume.position.description,
                'requirements': resume.position.requirements or {}
            }
        
        # 创建会话（使用新的 InterviewSession 模型）
        session = InterviewSession.objects.create(
            resume=resume
        )
        
        # 更新简历状态为面试中
        resume.update_status(Resume.Status.INTERVIEWING)
        
        # 构建简历摘要
        resume_summary = {
            'candidate_name': resume.candidate_name,
            'position_title': resume.position.title if resume.position else None,
        }
        if resume.screening_result:
            resume_summary['screening_score'] = resume.screening_result.get('score')
            resume_summary['screening_summary'] = resume.screening_result.get('summary', '')[:200]
        
        return ApiResponse.created(
            data={
                'session_id': str(session.id),
                'candidate_name': resume.candidate_name,
                'position_title': job_config.get('title'),
                'created_at': session.created_at.isoformat(),
                'resume_summary': resume_summary
            },
            message='面试辅助会话已创建'
        )


class SessionDetailView(SafeAPIView):
    """
    面试会话详情API
    GET: 获取会话详情
    DELETE: 删除会话
    """
    
    @extend_schema(
        summary="获取会话详情",
        description="获取指定面试会话的详细信息",
        responses={200: api_response(SessionDetailSerializer(), "SessionDetail")},
        tags=["interviews"],
    )
    def handle_get(self, request, session_id):
        """获取会话详情。"""
        session = self.get_object_or_404(InterviewSession, id=session_id)
        resume = session.resume
        
        # 从 resume.position 获取岗位信息
        position_title = resume.position.title if resume and resume.position else ''
        
        response_data = {
            'session_id': str(session.id),
            'candidate_name': resume.candidate_name if resume else '',
            'position_title': position_title,
            'qa_count': len(session.qa_records) if session.qa_records else 0,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat()
        }
        
        if session.final_report:
            response_data['has_final_report'] = True
            response_data['final_report_summary'] = session.final_report.get(
                'overall_assessment', {}
            ).get('summary', '')
        
        return ApiResponse.success(data=response_data)
    
    @extend_schema(
        summary="删除会话",
        description="删除指定的面试会话",
        responses={200: success_response("SessionDelete")},
        tags=["interviews"],
    )
    def handle_delete(self, request, session_id):
        """删除会话。"""
        session = self.get_object_or_404(InterviewSession, id=session_id)
        session.delete()
        
        return ApiResponse.success(message='会话已删除')


class GenerateQuestionsView(SafeAPIView):
    """
    生成问题API
    POST: 生成候选问题（临时生成，不保存到数据库）
    """
    
    @extend_schema(
        summary="生成候选问题",
        description="根据简历和岗位要求生成候选面试问题",
        request=GenerateQuestionsRequestSerializer,
        responses={200: api_response(GenerateQuestionsResponseSerializer(), "GenerateQuestions")},
        tags=["interviews"],
    )
    def handle_post(self, request, session_id):
        """生成候选问题。"""
        session = self.get_object_or_404(InterviewSession, id=session_id)
        resume = session.resume
        
        categories = self.get_param(request, 'categories', default=['简历相关', '专业能力', '行为面试'])
        candidate_level = self.get_param(request, 'candidate_level', default='senior')
        count_per_category = self.get_int_param(request, 'count_per_category', default=2)
        focus_on_resume = self.get_param(request, 'focus_on_resume', default=True)
        interest_point_count = self.get_int_param(request, 'interest_point_count', default=2)
        
        # 限制兴趣点数量在 1-3 之间
        interest_point_count = max(1, min(3, interest_point_count))
        
        # 从 resume.position 获取岗位配置
        job_config = {}
        if resume and resume.position:
            job_config = {
                'title': resume.position.title,
                'description': resume.position.description,
                'requirements': resume.position.requirements or {}
            }
        
        assistant = InterviewAssistAgent(job_config=job_config)
        
        all_questions = []
        interest_points = []
        
        # 生成基于简历的问题和兴趣点
        if focus_on_resume and resume and resume.content:
            result = assistant.generate_resume_based_questions(
                resume_content=resume.content,
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
        
        return ApiResponse.success(
            data={
                'session_id': str(session.id),
                'question_pool': all_questions,
                'resume_highlights': resume_highlights,
                'interest_points': interest_points  # 新格式：包含 content 和 question
            },
            message=f'已生成{len(all_questions)}个候选问题'
        )


class RecordQAView(SafeAPIView):
    """
    记录问答API
    POST: 记录问答并获取评估
    """
    
    @extend_schema(
        summary="记录问答并生成候选提问",
        description="记录面试问答，可选评估回答，并生成候选提问",
        request=RecordQARequestSerializer,
        responses={200: api_response(RecordQAResponseSerializer(), "RecordQA")},
        tags=["interviews"],
    )
    def handle_post(self, request, session_id):
        """记录问答并生成候选提问。"""
        session = self.get_object_or_404(InterviewSession, id=session_id)
        resume = session.resume
        
        question_data = self.get_param(request, 'question', default={})
        answer_data = self.get_param(request, 'answer', default={})
        skip_evaluation = self.get_param(request, 'skip_evaluation', default=True)  # 默认跳过评估
        followup_count = self.get_int_param(request, 'followup_count', default=2)  # 追问问题数量
        alternative_count = self.get_int_param(request, 'alternative_count', default=3)  # 候选问题数量
        
        if not question_data.get('content') or not answer_data.get('content'):
            raise ValidationException("缺少问题或回答内容")
        
        # 从 resume.position 获取岗位配置
        job_config = {}
        if resume and resume.position:
            job_config = {
                'title': resume.position.title,
                'description': resume.position.description,
                'requirements': resume.position.requirements or {}
            }
        
        assistant = InterviewAssistAgent(job_config=job_config)
        
        # 获取简历摘要
        resume_summary = ""
        if resume:
            position_title = resume.position.title if resume.position else '未指定'
            resume_summary = f"""候选人: {resume.candidate_name}
应聘岗位: {position_title}
简历内容摘要: {resume.content[:1000] if resume.content else '无'}"""
        
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
        qa_records = session.qa_records or []
        qa_records.append({
            'round': len(qa_records) + 1,
            'question': question_data['content'],
            'answer': answer_data['content'],
            'evaluation': evaluation  # 可能为 None
        })
        session.qa_records = qa_records
        session.save()
        
        round_number = len(qa_records)
        
        # 生成HR提示
        hr_hints = []
        if evaluation:
            hr_hints = self._generate_hr_hints(evaluation)
        else:
            hr_hints = ["请根据候选问题继续提问"]
        
        return ApiResponse.success(
            data={
                'round_number': round_number,
                'evaluation': evaluation,  # 可能为 None
                'candidate_questions': candidate_questions,  # 新增：LLM生成的候选问题
                'hr_action_hints': hr_hints
            },
            message='问答已记录，候选问题已生成'
        )
    
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
    
    @extend_schema(
        summary="生成面试报告",
        description="根据问答记录生成最终面试评估报告",
        request=GenerateReportRequestSerializer,
        responses={200: api_response(InterviewReportResponseSerializer(), "GenerateReport")},
        tags=["interviews"],
    )
    def handle_post(self, request, session_id):
        """生成最终报告。"""
        session = self.get_object_or_404(InterviewSession, id=session_id)
        resume = session.resume
        
        include_conversation_log = self.get_param(request, 'include_conversation_log', default=True)
        hr_notes = self.get_param(request, 'hr_notes', default='')
        
        qa_records = session.qa_records or []
        
        if not qa_records:
            raise ValidationException("没有问答记录，无法生成报告")
        
        # 从 resume.position 获取岗位配置
        job_config = {}
        if resume and resume.position:
            job_config = {
                'title': resume.position.title,
                'description': resume.position.description,
                'requirements': resume.position.requirements or {}
            }
        
        assistant = InterviewAssistAgent(job_config=job_config)
        
        # 生成报告
        candidate_name = resume.candidate_name if resume else '未知'
        report = assistant.generate_final_report(
            candidate_name=candidate_name,
            qa_records=qa_records,
            hr_notes=hr_notes
        )
        
        # 保存报告到 final_report JSON
        session.final_report = report
        session.save()
        
        return ApiResponse.success(
            data={
                'report': report,
            },
            message='评估报告生成成功'
        )
    
