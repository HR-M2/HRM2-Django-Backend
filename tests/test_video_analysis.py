"""
视频分析模块的测试。
"""
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.video_analysis.models import VideoAnalysis
from apps.resume.models import Resume
from apps.position_settings.models import Position


class VideoAnalysisModelTest(TestCase):
    """视频分析模型的测试。"""
    
    def setUp(self):
        """创建测试数据"""
        self.position = Position.objects.create(
            title="Python开发工程师",
            department="技术部"
        )
        self.resume = Resume.objects.create(
            filename="test.pdf",
            file_hash="testhash123",
            candidate_name="张三",
            content="测试简历内容",
            position=self.position
        )
    
    def test_create_video_analysis(self):
        """测试创建视频分析记录。"""
        video_file = SimpleUploadedFile("test_video.mp4", b"fake content")
        analysis = VideoAnalysis.objects.create(
            resume=self.resume,
            video_file=video_file,
            video_name="test_video.mp4",
            status='pending'
        )
        
        self.assertIsNotNone(analysis.id)
        self.assertEqual(analysis.candidate_name, "张三")  # 从resume获取
        self.assertEqual(analysis.status, 'pending')
    
    def test_analysis_result_json_field(self):
        """测试analysis_result JSON字段。"""
        video_file = SimpleUploadedFile("test.mp4", b"fake content")
        analysis = VideoAnalysis.objects.create(
            resume=self.resume,
            video_file=video_file,
            video_name="test.mp4",
            analysis_result={
                "personality": {"extraversion": 0.75},
                "fraud_score": 0.15,
                "confidence_score": 0.85
            }
        )
        
        result = analysis.analysis_result
        
        self.assertEqual(result['fraud_score'], 0.15)
        self.assertEqual(result['personality']['extraversion'], 0.75)


class VideoAnalysisAPITest(TestCase):
    """视频分析API端点的测试。"""
    
    def setUp(self):
        self.client = Client()
        self.position = Position.objects.create(
            title="Python开发工程师",
            department="技术部"
        )
        self.resume = Resume.objects.create(
            filename="test.pdf",
            file_hash="apitesthash",
            candidate_name="候选人A",
            content="测试简历内容",
            position=self.position
        )
    
    def test_get_video_list(self):
        """测试获取视频分析列表。"""
        # 创建测试数据
        video_file = SimpleUploadedFile("test1.mp4", b"fake content")
        VideoAnalysis.objects.create(
            resume=self.resume,
            video_file=video_file,
            video_name="test1.mp4",
            status='completed'
        )
        
        response = self.client.get('/api/videos/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # 统一响应格式: {'code': 200, 'message': '...', 'data': {...}}
        self.assertEqual(data['code'], 200)
        self.assertIn('data', data)
        # 视频列表返回格式包含 videos, total, page, page_size
        self.assertIn('videos', data['data'])
        self.assertIn('total', data['data'])
    
    def test_get_video_status_not_found(self):
        """测试获取不存在的视频状态。"""
        response = self.client.get('/api/videos/00000000-0000-0000-0000-000000000000/status/')
        
        self.assertEqual(response.status_code, 404)
