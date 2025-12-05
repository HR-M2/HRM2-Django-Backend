"""
岗位设置API视图模块 - 与原版 RecruitmentSystemAPI 返回格式保持一致。
"""
import os
import json
import logging
from django.conf import settings
from django.http import JsonResponse

from apps.common.mixins import SafeAPIView
from apps.common.exceptions import ValidationException, NotFoundException

from .models import PositionCriteria

logger = logging.getLogger(__name__)


class RecruitmentCriteriaView(SafeAPIView):
    """
    招聘标准API
    GET: 获取当前招聘标准
    POST: 更新招聘标准
    """
    
    # 默认标准文件路径（用于向后兼容）- 与原版路径一致
    CRITERIA_FILE = os.path.join('apps', 'position_settings', 'migrations', 'recruitment_criteria.json')
    
    def handle_get(self, request):
        """获取招聘标准。"""
        # 首先尝试从文件获取（与原版一致）
        file_path = os.path.join(settings.BASE_DIR, self.CRITERIA_FILE)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 返回与原版完全一致的格式
                return JsonResponse({'code': 200, 'message': '成功', 'data': data})
            except json.JSONDecodeError:
                return JsonResponse({'code': 500, 'message': '文件格式错误，非有效JSON'}, status=500)
            except Exception as e:
                logger.error(f"Failed to read criteria file: {e}")
                return JsonResponse({'code': 500, 'message': f'服务器内部错误: {str(e)}'}, status=500)
        
        # 尝试从数据库获取
        criteria = PositionCriteria.objects.filter(is_active=True).first()
        if criteria:
            return JsonResponse({'code': 200, 'message': '成功', 'data': criteria.to_dict()})
        
        # 返回默认标准
        default_criteria = self._get_default_criteria()
        return JsonResponse({'code': 200, 'message': '成功', 'data': default_criteria})
    
    def handle_post(self, request):
        """更新招聘标准。"""
        data = request.data
        
        if not data:
            raise ValidationException("请求数据不能为空")
        
        # 验证必填字段
        required_fields = ['position']
        for field in required_fields:
            if field not in data:
                raise ValidationException(f"缺少必要字段: {field}")
        
        # 保存到数据库
        criteria, created = PositionCriteria.objects.update_or_create(
            position=data.get('position'),
            defaults={
                'required_skills': data.get('required_skills', []),
                'optional_skills': data.get('optional_skills', []),
                'min_experience': data.get('min_experience', 0),
                'education': data.get('education', []),
                'certifications': data.get('certifications', []),
                'salary_min': data.get('salary_range', [0, 0])[0] if data.get('salary_range') else 0,
                'salary_max': data.get('salary_range', [0, 0])[1] if len(data.get('salary_range', [])) > 1 else 0,
                'project_requirements': data.get('project_requirements', {}),
                'is_active': True
            }
        )
        
        # 同时保存到文件以保持向后兼容
        try:
            file_path = os.path.join(settings.BASE_DIR, self.CRITERIA_FILE)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save criteria to file: {e}")
        
        # 返回与原版一致的格式
        return JsonResponse({'code': 200, 'message': '招聘标准更新成功', 'data': criteria.to_dict()})
    
    def _get_default_criteria(self):
        """获取默认招聘标准。"""
        return {
            "position": "Python开发工程师",
            "required_skills": ["Python", "Django", "MySQL", "Linux"],
            "optional_skills": ["Redis", "Docker", "Vue.js", "AI"],
            "min_experience": 2,
            "education": ["本科", "硕士"],
            "certifications": [],
            "salary_range": [8000, 20000],
            "project_requirements": {
                "min_projects": 2,
                "team_lead_experience": True
            }
        }


class PositionCriteriaListView(SafeAPIView):
    """
    岗位标准列表API
    GET: 获取所有岗位标准列表
    POST: 创建新岗位
    """
    
    def handle_get(self, request):
        """获取所有岗位标准。"""
        include_resumes = request.GET.get('include_resumes', 'false').lower() == 'true'
        criteria_list = PositionCriteria.objects.filter(is_active=True)
        
        data = []
        for c in criteria_list:
            item = c.to_dict()
            if include_resumes:
                # 获取分配到该岗位的简历
                resumes = c.get_assigned_resumes()
                item['resumes'] = [
                    {
                        'id': str(r.id),
                        'candidate_name': r.candidate_name,
                        'position_title': r.position_title,
                        'resume_content': r.resume_content,
                        'screening_score': r.screening_score,
                        'screening_summary': r.screening_summary,
                        'created_at': r.created_at.isoformat() if r.created_at else None
                    }
                    for r in resumes
                ]
            data.append(item)
        
        return JsonResponse({
            'code': 200, 
            'message': '成功', 
            'data': {
                'positions': data,
                'total': len(data)
            }
        })
    
    def handle_post(self, request):
        """创建新岗位。"""
        data = request.data
        
        if not data:
            raise ValidationException("请求数据不能为空")
        
        position_name = data.get('position')
        if not position_name:
            raise ValidationException("岗位名称不能为空")
        
        # 检查是否已存在同名岗位
        if PositionCriteria.objects.filter(position=position_name, is_active=True).exists():
            raise ValidationException(f"岗位 '{position_name}' 已存在")
        
        criteria = PositionCriteria.objects.create(
            position=position_name,
            department=data.get('department', ''),
            description=data.get('description', ''),
            required_skills=data.get('required_skills', []),
            optional_skills=data.get('optional_skills', []),
            min_experience=data.get('min_experience', 0),
            education=data.get('education', []),
            certifications=data.get('certifications', []),
            salary_min=data.get('salary_range', [0, 0])[0] if data.get('salary_range') else 0,
            salary_max=data.get('salary_range', [0, 0])[1] if len(data.get('salary_range', [])) > 1 else 0,
            project_requirements=data.get('project_requirements', {}),
            is_active=True
        )
        
        return JsonResponse({
            'code': 201, 
            'message': '岗位创建成功', 
            'data': criteria.to_dict()
        }, status=201)


class PositionCriteriaDetailView(SafeAPIView):
    """
    单个岗位API
    GET: 获取岗位详情
    PUT: 更新岗位
    DELETE: 删除岗位（软删除）
    """
    
    def handle_get(self, request, position_id):
        """获取岗位详情。"""
        try:
            criteria = PositionCriteria.objects.get(id=position_id, is_active=True)
        except PositionCriteria.DoesNotExist:
            raise NotFoundException(f"岗位不存在: {position_id}")
        
        data = criteria.to_dict()
        
        # 获取分配的简历
        include_resumes = request.GET.get('include_resumes', 'true').lower() == 'true'
        if include_resumes:
            resumes = criteria.get_assigned_resumes()
            data['resumes'] = [
                {
                    'id': str(r.id),
                    'candidate_name': r.candidate_name,
                    'position_title': r.position_title,
                    'resume_content': r.resume_content[:200] + '...' if r.resume_content and len(r.resume_content) > 200 else r.resume_content,
                    'screening_score': r.screening_score,
                    'screening_summary': r.screening_summary,
                    'created_at': r.created_at.isoformat() if r.created_at else None
                }
                for r in resumes
            ]
        
        return JsonResponse({'code': 200, 'message': '成功', 'data': data})
    
    def handle_put(self, request, position_id):
        """更新岗位。"""
        try:
            criteria = PositionCriteria.objects.get(id=position_id, is_active=True)
        except PositionCriteria.DoesNotExist:
            raise NotFoundException(f"岗位不存在: {position_id}")
        
        data = request.data
        if not data:
            raise ValidationException("请求数据不能为空")
        
        # 更新字段
        if 'position' in data:
            criteria.position = data['position']
        if 'department' in data:
            criteria.department = data['department']
        if 'description' in data:
            criteria.description = data['description']
        if 'required_skills' in data:
            criteria.required_skills = data['required_skills']
        if 'optional_skills' in data:
            criteria.optional_skills = data['optional_skills']
        if 'min_experience' in data:
            criteria.min_experience = data['min_experience']
        if 'education' in data:
            criteria.education = data['education']
        if 'certifications' in data:
            criteria.certifications = data['certifications']
        if 'salary_range' in data and len(data['salary_range']) >= 2:
            criteria.salary_min = data['salary_range'][0]
            criteria.salary_max = data['salary_range'][1]
        if 'project_requirements' in data:
            criteria.project_requirements = data['project_requirements']
        
        criteria.save()
        
        return JsonResponse({'code': 200, 'message': '岗位更新成功', 'data': criteria.to_dict()})
    
    def handle_delete(self, request, position_id):
        """删除岗位（软删除）。"""
        try:
            criteria = PositionCriteria.objects.get(id=position_id, is_active=True)
        except PositionCriteria.DoesNotExist:
            raise NotFoundException(f"岗位不存在: {position_id}")
        
        criteria.is_active = False
        criteria.save()
        
        return JsonResponse({'code': 200, 'message': '岗位已删除'})


class PositionAssignResumesView(SafeAPIView):
    """
    岗位简历分配API
    POST: 将简历分配到岗位
    """
    
    def handle_post(self, request, position_id):
        """将简历分配到岗位。"""
        from apps.resume_screening.models import ResumeData
        from .models import ResumePositionAssignment
        
        try:
            position = PositionCriteria.objects.get(id=position_id, is_active=True)
        except PositionCriteria.DoesNotExist:
            raise NotFoundException(f"岗位不存在: {position_id}")
        
        data = request.data
        resume_ids = data.get('resume_data_ids', [])
        
        if not resume_ids:
            raise ValidationException("请提供要分配的简历ID列表")
        
        assigned_count = 0
        skipped_count = 0
        
        for resume_id in resume_ids:
            try:
                resume = ResumeData.objects.get(id=resume_id)
                # 检查是否已分配
                assignment, created = ResumePositionAssignment.objects.get_or_create(
                    position=position,
                    resume_data=resume,
                    defaults={'notes': data.get('notes', '')}
                )
                if created:
                    assigned_count += 1
                else:
                    skipped_count += 1
            except ResumeData.DoesNotExist:
                logger.warning(f"简历不存在: {resume_id}")
                continue
        
        # 更新简历数量
        position.update_resume_count()
        
        return JsonResponse({
            'code': 200,
            'message': f'成功分配 {assigned_count} 份简历，跳过 {skipped_count} 份已分配简历',
            'data': {
                'position_id': str(position.id),
                'assigned_count': assigned_count,
                'skipped_count': skipped_count,
                'total_resumes': position.resume_count
            }
        })


class PositionRemoveResumeView(SafeAPIView):
    """
    从岗位移除简历API
    DELETE: 从岗位移除指定简历
    """
    
    def handle_delete(self, request, position_id, resume_id):
        """从岗位移除简历。"""
        from .models import ResumePositionAssignment
        
        try:
            position = PositionCriteria.objects.get(id=position_id, is_active=True)
        except PositionCriteria.DoesNotExist:
            raise NotFoundException(f"岗位不存在: {position_id}")
        
        try:
            assignment = ResumePositionAssignment.objects.get(
                position=position,
                resume_data_id=resume_id
            )
            assignment.delete()
            
            # 更新简历数量
            position.update_resume_count()
            
            return JsonResponse({
                'code': 200,
                'message': '简历已从岗位移除',
                'data': {
                    'position_id': str(position.id),
                    'resume_id': str(resume_id),
                    'total_resumes': position.resume_count
                }
            })
        except ResumePositionAssignment.DoesNotExist:
            raise NotFoundException(f"该简历未分配到此岗位")


class PositionAIGenerateView(SafeAPIView):
    """
    AI生成岗位要求API
    POST: 根据描述和文档生成岗位要求
    """
    
    def handle_post(self, request):
        """根据用户输入生成岗位要求。"""
        from services.agents import get_position_ai_service
        
        data = request.data
        description = data.get('description', '')
        documents = data.get('documents', [])
        
        if not description:
            raise ValidationException("请提供岗位描述")
        
        try:
            service = get_position_ai_service()
            result = service.generate_position_requirements(
                description=description,
                documents=documents
            )
            
            return JsonResponse({
                'code': 200,
                'message': '生成成功',
                'data': result
            })
        except ValueError as e:
            return JsonResponse({
                'code': 400,
                'message': str(e),
                'data': None
            }, status=400)
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return JsonResponse({
                'code': 500,
                'message': f'AI生成失败: {str(e)}',
                'data': None
            }, status=500)
