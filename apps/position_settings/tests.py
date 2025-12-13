"""
岗位模型单元测试
"""
from django.test import TestCase
from apps.position_settings.models import Position


class PositionModelTest(TestCase):
    """Position 模型测试"""
    
    def setUp(self):
        """测试前创建测试数据"""
        self.position = Position.objects.create(
            title="Python开发工程师",
            department="技术部",
            description="负责后端开发",
            requirements={
                "required_skills": ["Python", "Django"],
                "optional_skills": ["React"],
                "min_experience": 3,
                "education": ["本科", "硕士"],
                "salary_range": [15000, 25000]
            }
        )
    
    def test_create_position(self):
        """测试创建岗位"""
        self.assertIsNotNone(self.position.id)
        self.assertEqual(self.position.title, "Python开发工程师")
        self.assertEqual(self.position.department, "技术部")
        self.assertTrue(self.position.is_active)
    
    def test_default_is_active_true(self):
        """测试默认启用状态"""
        self.assertTrue(self.position.is_active)
    
    def test_requirements_json_field(self):
        """测试requirements JSON字段"""
        reqs = self.position.requirements
        self.assertIn("Python", reqs['required_skills'])
        self.assertEqual(reqs['min_experience'], 3)
        self.assertEqual(reqs['salary_range'], [15000, 25000])
    
    def test_to_dict(self):
        """测试转换为字典"""
        data = self.position.to_dict()
        
        self.assertEqual(data['title'], "Python开发工程师")
        self.assertEqual(data['position'], "Python开发工程师")  # 兼容字段
        self.assertEqual(data['department'], "技术部")
        self.assertIn("Python", data['required_skills'])
        self.assertEqual(data['min_experience'], 3)
        self.assertEqual(data['salary_min'], 15000)
        self.assertEqual(data['salary_max'], 25000)
    
    def test_get_resume_count(self):
        """测试获取简历数量"""
        from apps.resume.models import Resume
        
        # 初始无简历
        self.assertEqual(self.position.get_resume_count(), 0)
        
        # 创建关联简历
        Resume.objects.create(
            filename="resume1.pdf",
            file_hash="hash1",
            candidate_name="张三",
            content="内容1",
            position=self.position
        )
        self.assertEqual(self.position.get_resume_count(), 1)
        
        Resume.objects.create(
            filename="resume2.pdf",
            file_hash="hash2",
            candidate_name="李四",
            content="内容2",
            position=self.position
        )
        self.assertEqual(self.position.get_resume_count(), 2)
    
    def test_from_legacy_data(self):
        """测试从旧格式数据创建岗位"""
        legacy_data = {
            "position": "前端开发工程师",
            "department": "产品部",
            "required_skills": ["JavaScript", "React"],
            "min_experience": 2,
            "salary_min": 12000,
            "salary_max": 20000
        }
        pos = Position.from_legacy_data(legacy_data)
        
        self.assertEqual(pos.title, "前端开发工程师")
        self.assertEqual(pos.department, "产品部")
        self.assertEqual(pos.requirements['required_skills'], ["JavaScript", "React"])
        self.assertEqual(pos.requirements['min_experience'], 2)
        self.assertEqual(pos.requirements['salary_range'], [12000, 20000])
    
    def test_str_representation(self):
        """测试字符串表示"""
        self.assertEqual(str(self.position), "Python开发工程师")
    
    def test_empty_requirements_default(self):
        """测试空requirements默认值"""
        pos = Position.objects.create(title="测试岗位")
        self.assertEqual(pos.requirements, {})
