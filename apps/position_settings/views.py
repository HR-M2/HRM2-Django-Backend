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
    """
    
    def handle_get(self, request):
        """获取所有岗位标准。"""
        criteria_list = PositionCriteria.objects.filter(is_active=True)
        
        data = [
            {
                'id': str(c.id),
                'position': c.position,
                'department': c.department,
                'min_experience': c.min_experience,
                'salary_range': [c.salary_min, c.salary_max],
                'created_at': c.created_at.isoformat()
            }
            for c in criteria_list
        ]
        
        # 返回与原版一致的格式
        return JsonResponse({'code': 200, 'message': '成功', 'data': data})
