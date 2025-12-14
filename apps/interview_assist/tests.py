"""
面试辅助模型单元测试
"""
from django.test import TestCase
from apps.interview_assist.models import InterviewSession
from apps.resume.models import Resume
from apps.position_settings.models import Position


class InterviewSessionModelTest(TestCase):
    """InterviewSession 模型测试"""
    
    def setUp(self):
        """测试前创建测试数据"""
        self.position = Position.objects.create(
            title="Python开发工程师",
            department="技术部",
            requirements={"required_skills": ["Python"]}
        )
        self.resume = Resume.objects.create(
            filename="test_resume.pdf",
            file_hash="abc123hash",
            candidate_name="张三",
            content="测试简历内容",
            position=self.position
        )
        self.session = InterviewSession.objects.create(
            resume=self.resume
        )
    
    def test_create_interview_session(self):
        """测试创建面试会话"""
        self.assertIsNotNone(self.session.id)
        self.assertEqual(self.session.resume, self.resume)
        self.assertEqual(self.session.qa_records, [])
    
    def test_current_round(self):
        """测试当前轮次"""
        self.assertEqual(self.session.current_round, 0)
        
        self.session.add_qa_record("问题1", "回答1")
        self.assertEqual(self.session.current_round, 1)
        
        self.session.add_qa_record("问题2", "回答2")
        self.assertEqual(self.session.current_round, 2)
    
    def test_is_completed(self):
        """测试完成状态"""
        self.assertFalse(self.session.is_completed)
        
        self.session.set_final_report({"summary": "面试表现良好"})
        self.assertTrue(self.session.is_completed)
    
    def test_job_config_property(self):
        """测试从关联简历获取岗位配置"""
        job_config = self.session.job_config
        self.assertEqual(job_config['title'], "Python开发工程师")
        self.assertIn("Python", job_config['required_skills'])
    
    def test_add_qa_record(self):
        """测试添加问答记录"""
        self.session.add_qa_record("请介绍一下自己", "我是张三...", {"score": 80})
        
        self.assertEqual(len(self.session.qa_records), 1)
        record = self.session.qa_records[0]
        self.assertEqual(record['round'], 1)
        self.assertEqual(record['question'], "请介绍一下自己")
        self.assertEqual(record['answer'], "我是张三...")
        self.assertEqual(record['evaluation']['score'], 80)
    
    def test_set_final_report(self):
        """测试设置最终报告"""
        report = {
            "summary": "面试表现良好",
            "score": 85,
            "recommendation": "推荐录用"
        }
        self.session.set_final_report(report)
        
        self.assertEqual(self.session.final_report, report)
        # 验证简历状态更新
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.status, Resume.Status.INTERVIEWING)
    
    def test_cascade_delete_on_resume(self):
        """测试删除简历时级联删除面试会话"""
        session_id = self.session.id
        self.resume.delete()
        
        # 面试会话应该被级联删除
        self.assertFalse(InterviewSession.objects.filter(id=session_id).exists())
    
    def test_str_representation(self):
        """测试字符串表示"""
        self.assertIn("张三", str(self.session))
        self.assertIn("进行中", str(self.session))
        
        self.session.set_final_report({"summary": "完成"})
        self.assertIn("已完成", str(self.session))
