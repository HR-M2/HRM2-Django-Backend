"""
简历模型单元测试
"""
from django.test import TestCase
from apps.resume.models import Resume
from apps.position_settings.models import Position


class ResumeModelTest(TestCase):
    """Resume 模型测试"""
    
    def setUp(self):
        """测试前创建测试数据"""
        self.position = Position.objects.create(
            title="Python开发工程师",
            department="技术部",
            requirements={"required_skills": ["Python"], "min_experience": 3}
        )
        self.resume = Resume.objects.create(
            filename="test_resume.pdf",
            file_hash="abc123hash",
            file_size=1024,
            file_type="application/pdf",
            candidate_name="张三",
            content="测试简历内容"
        )
    
    def test_create_resume(self):
        """测试创建简历"""
        self.assertIsNotNone(self.resume.id)
        self.assertEqual(self.resume.filename, "test_resume.pdf")
        self.assertEqual(self.resume.candidate_name, "张三")
        self.assertEqual(self.resume.status, Resume.Status.PENDING)
    
    def test_default_status_pending(self):
        """测试默认状态为待筛选"""
        self.assertEqual(self.resume.status, Resume.Status.PENDING)
    
    def test_file_hash_unique(self):
        """测试文件哈希唯一性"""
        with self.assertRaises(Exception):
            Resume.objects.create(
                filename="duplicate.pdf",
                file_hash="abc123hash",  # 重复哈希
                candidate_name="李四",
                content="另一份简历"
            )
    
    def test_assign_to_position(self):
        """测试分配到岗位"""
        self.resume.assign_to_position(self.position)
        self.assertEqual(self.resume.position, self.position)
        self.assertEqual(self.resume.position.title, "Python开发工程师")
    
    def test_unassign_position(self):
        """测试取消岗位分配"""
        self.resume.assign_to_position(self.position)
        self.resume.unassign_position()
        self.assertIsNone(self.resume.position)
    
    def test_update_status(self):
        """测试更新状态"""
        self.resume.update_status(Resume.Status.SCREENED)
        self.assertEqual(self.resume.status, Resume.Status.SCREENED)
        
        self.resume.update_status(Resume.Status.INTERVIEWING)
        self.assertEqual(self.resume.status, Resume.Status.INTERVIEWING)
        
        self.resume.update_status(Resume.Status.ANALYZED)
        self.assertEqual(self.resume.status, Resume.Status.ANALYZED)
    
    def test_set_screening_result(self):
        """测试设置筛选结果"""
        result = {"score": 85, "dimensions": {"skill": 90}}
        report = "# 筛选报告\n分数: 85"
        self.resume.set_screening_result(result, report)
        
        self.assertEqual(self.resume.screening_result, result)
        self.assertEqual(self.resume.screening_report, report)
        self.assertEqual(self.resume.status, Resume.Status.SCREENED)
    
    def test_to_dict(self):
        """测试转换为字典"""
        self.resume.assign_to_position(self.position)
        data = self.resume.to_dict()
        
        self.assertEqual(data['filename'], "test_resume.pdf")
        self.assertEqual(data['candidate_name'], "张三")
        self.assertEqual(data['position_title'], "Python开发工程师")
        self.assertTrue(data['is_assigned'])
        self.assertFalse(data['is_screened'])
    
    def test_cascade_delete_on_position_set_null(self):
        """测试删除岗位时简历保留但position置空"""
        self.resume.assign_to_position(self.position)
        position_id = self.position.id
        self.position.delete()
        
        self.resume.refresh_from_db()
        self.assertIsNone(self.resume.position)
        self.assertIsNotNone(self.resume.id)  # 简历仍存在
    
    def test_str_representation(self):
        """测试字符串表示"""
        self.assertEqual(str(self.resume), "test_resume.pdf - 张三")
