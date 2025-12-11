"""
视频分析模块的测试。
"""
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.video_analysis.models import VideoAnalysis
from apps.video_analysis.services import VideoAnalysisService


class VideoAnalysisModelTest(TestCase):
    """视频分析模型的测试。"""
    
    def test_create_video_analysis(self):
        """测试创建视频分析记录。"""
        analysis = VideoAnalysis.objects.create(
            video_name="test_video.mp4",
            candidate_name="张三",
            position_applied="Python开发工程师",
            status='pending'
        )
        
        self.assertIsNotNone(analysis.id)
        self.assertEqual(analysis.candidate_name, "张三")
        self.assertEqual(analysis.status, 'pending')
    
    def test_analysis_result_property(self):
        """测试analysis_result属性。"""
        analysis = VideoAnalysis.objects.create(
            video_name="test.mp4",
            candidate_name="李四",
            position_applied="开发工程师",
            fraud_score=0.15,
            extraversion_score=0.75,
            conscientiousness_score=0.85
        )
        
        result = analysis.analysis_result
        
        self.assertEqual(result['fraud_score'], 0.15)
        self.assertEqual(result['extraversion_score'], 0.75)


class VideoAnalysisServiceTest(TestCase):
    """VideoAnalysisService的测试。"""
    
    def test_simulate_analysis(self):
        """测试模拟分析返回有效分数。"""
        result = VideoAnalysisService._simulate_analysis()
        
        self.assertIn('fraud_score', result)
        self.assertIn('extraversion_score', result)
        self.assertIn('conscientiousness_score', result)
        
        # 分数应在有效范围内
        self.assertGreaterEqual(result['fraud_score'], 0)
        self.assertLessEqual(result['fraud_score'], 1)
    
    def test_update_analysis_result(self):
        """测试更新分析结果。"""
        analysis = VideoAnalysis.objects.create(
            video_name="test.mp4",
            candidate_name="王五",
            position_applied="开发工程师",
            status='processing'
        )
        
        updated = VideoAnalysisService.update_analysis_result(
            str(analysis.id),
            fraud_score=0.2,
            extraversion_score=0.8,
            status='completed'
        )
        
        self.assertEqual(updated.fraud_score, 0.2)
        self.assertEqual(updated.extraversion_score, 0.8)
        self.assertEqual(updated.status, 'completed')


class VideoAnalysisAPITest(TestCase):
    """视频分析API端点的测试。"""
    
    def setUp(self):
        self.client = Client()
    
    def test_get_video_list(self):
        """测试获取视频分析列表。"""
        # 创建测试数据
        VideoAnalysis.objects.create(
            video_name="test1.mp4",
            candidate_name="候选人A",
            position_applied="开发工程师",
            status='completed'
        )
        
        response = self.client.get('/api/videos/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # 视频列表返回格式包含 videos, total, page, page_size
        self.assertIn('videos', data)
        self.assertIn('total', data)
    
    def test_get_video_status_not_found(self):
        """测试获取不存在的视频状态。"""
        response = self.client.get('/api/videos/00000000-0000-0000-0000-000000000000/status/')
        
        self.assertEqual(response.status_code, 404)
