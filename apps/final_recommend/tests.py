"""
综合分析模型单元测试
"""
from django.test import TestCase
from apps.final_recommend.models import ComprehensiveAnalysis
from apps.resume.models import Resume
from apps.position_settings.models import Position


class ComprehensiveAnalysisModelTest(TestCase):
    """ComprehensiveAnalysis 模型测试"""
    
    def setUp(self):
        """测试前创建测试数据"""
        self.position = Position.objects.create(
            title="Python开发工程师",
            department="技术部"
        )
        self.resume = Resume.objects.create(
            filename="test_resume.pdf",
            file_hash="abc123hash",
            candidate_name="张三",
            content="测试简历内容",
            position=self.position
        )
        self.analysis = ComprehensiveAnalysis.objects.create(
            resume=self.resume,
            final_score=85.5,
            recommendation={
                "level": "A",
                "label": "强烈推荐",
                "action": "建议尽快发放offer"
            },
            dimension_scores={
                "technical": 90,
                "communication": 80,
                "experience": 85
            },
            report="# 综合分析报告\n该候选人表现优秀..."
        )
    
    def test_create_comprehensive_analysis(self):
        """测试创建综合分析"""
        self.assertIsNotNone(self.analysis.id)
        self.assertEqual(self.analysis.resume, self.resume)
        self.assertEqual(self.analysis.final_score, 85.5)
    
    def test_recommendation_json_field(self):
        """测试recommendation JSON字段"""
        rec = self.analysis.recommendation
        self.assertEqual(rec['level'], "A")
        self.assertEqual(rec['label'], "强烈推荐")
    
    def test_recommendation_level_property(self):
        """测试兼容属性 recommendation_level"""
        self.assertEqual(self.analysis.recommendation_level, "A")
    
    def test_recommendation_label_property(self):
        """测试兼容属性 recommendation_label"""
        self.assertEqual(self.analysis.recommendation_label, "强烈推荐")
    
    def test_recommendation_action_property(self):
        """测试兼容属性 recommendation_action"""
        self.assertEqual(self.analysis.recommendation_action, "建议尽快发放offer")
    
    def test_comprehensive_report_property(self):
        """测试兼容属性 comprehensive_report"""
        self.assertEqual(self.analysis.comprehensive_report, self.analysis.report)
    
    def test_dimension_scores(self):
        """测试维度评分"""
        scores = self.analysis.dimension_scores
        self.assertEqual(scores['technical'], 90)
        self.assertEqual(scores['communication'], 80)
        self.assertEqual(scores['experience'], 85)
    
    def test_set_result(self):
        """测试设置分析结果"""
        new_recommendation = {
            "level": "B",
            "label": "推荐",
            "action": "可以进入下一轮"
        }
        new_scores = {"technical": 75, "communication": 85}
        
        self.analysis.set_result(
            score=78.0,
            recommendation=new_recommendation,
            dimension_scores=new_scores,
            report="更新后的报告"
        )
        
        self.assertEqual(self.analysis.final_score, 78.0)
        self.assertEqual(self.analysis.recommendation['level'], "B")
        # 验证简历状态更新
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.status, Resume.Status.ANALYZED)
    
    def test_cascade_delete_on_resume(self):
        """测试删除简历时级联删除综合分析"""
        analysis_id = self.analysis.id
        self.resume.delete()
        
        # 综合分析应该被级联删除
        self.assertFalse(ComprehensiveAnalysis.objects.filter(id=analysis_id).exists())
    
    def test_str_representation(self):
        """测试字符串表示"""
        self.assertIn("张三", str(self.analysis))
        self.assertIn("强烈推荐", str(self.analysis))
