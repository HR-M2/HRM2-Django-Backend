"""
简历筛选模块的测试。
"""
import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse

from apps.resume_screening.models import ScreeningTask
from apps.position_settings.models import Position
from apps.resume_screening.services import ScreeningService


class ScreeningTaskModelTest(TestCase):
    """筛选任务模型的测试。"""
    
    def setUp(self):
        """创建测试岗位"""
        self.position = Position.objects.create(
            title="Python开发工程师",
            department="技术部"
        )
    
    def test_create_task(self):
        """测试创建筛选任务。"""
        task = ScreeningTask.objects.create(
            position=self.position,
            status='pending',
            progress=0,
            total_count=1
        )
        
        self.assertIsNotNone(task.id)
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.progress, 0)
    
    def test_task_status_choices(self):
        """测试任务状态选项。"""
        task = ScreeningTask.objects.create(position=self.position, status='running')
        self.assertEqual(task.status, 'running')
        
        task.status = 'completed'
        task.save()
        self.assertEqual(task.status, 'completed')


class ScreeningServiceTest(TestCase):
    """ScreeningService的测试。"""
    
    def test_parse_input_data_valid(self):
        """测试解析有效的输入数据。"""
        data = {
            "position": {
                "title": "Python Developer",
                "required_skills": ["Python", "Django"]
            },
            "resumes": [
                {"name": "test.pdf", "content": "Resume content here"}
            ]
        }
        
        position, resumes = ScreeningService.parse_input_data(data)
        
        self.assertEqual(position['title'], "Python Developer")
        self.assertEqual(len(resumes), 1)
        self.assertEqual(resumes[0]['name'], "test.pdf")
    
    def test_parse_input_data_missing_position(self):
        """测试解析缺少岗位信息的数据。"""
        from apps.common.exceptions import ValidationException
        
        data = {
            "resumes": [{"name": "test.pdf", "content": "content"}]
        }
        
        with self.assertRaises(ValidationException):
            ScreeningService.parse_input_data(data)
    
    def test_extract_scores_hr(self):
        """测试从对话中提取HR评分。"""
        conversation = [
            {
                "name": "HR_Expert",
                "content": "HR评分：85分，理由：经验丰富，建议月薪：15000"
            }
        ]
        
        result = ScreeningService.extract_scores_and_comments(conversation)
        
        self.assertEqual(result['scores']['hr_score'], 85.0)
        self.assertEqual(result['salary_suggestions']['hr_suggestion'], '15000')


class ResumeScreeningAPITest(TestCase):
    """简历筛选API端点的测试。"""
    
    def setUp(self):
        self.client = Client()
    
    @patch('threading.Thread')
    def test_submit_screening_task(self, mock_thread):
        """测试提交筛选任务。
        
        使用 mock 阻止后台线程执行，避免 SQLite 并发写入问题。
        """
        # Mock Thread 不启动实际线程
        mock_thread.return_value.start.return_value = None
        
        data = {
            "position": {
                "title": "Python Developer",
                "required_skills": ["Python"]
            },
            "resumes": [
                {"name": "test.pdf", "content": "Python developer with 3 years experience"}
            ]
        }
        
        response = self.client.post(
            '/api/screening/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertIn(response.status_code, [200, 201, 202])
    
    def test_get_task_status_not_found(self):
        """测试获取不存在的任务状态。"""
        response = self.client.get('/api/screening/tasks/00000000-0000-0000-0000-000000000000/status/')
        
        self.assertEqual(response.status_code, 404)


