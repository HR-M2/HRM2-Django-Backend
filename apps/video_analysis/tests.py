"""
视频分析模型单元测试
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.video_analysis.models import VideoAnalysis
from apps.resume.models import Resume
from apps.position_settings.models import Position


class VideoAnalysisModelTest(TestCase):
    """VideoAnalysis 模型测试"""
    
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
        # 创建一个模拟视频文件
        video_content = b'fake video content'
        video_file = SimpleUploadedFile("test_video.mp4", video_content)
        self.video_analysis = VideoAnalysis.objects.create(
            resume=self.resume,
            video_file=video_file,
            video_name="面试视频1.mp4"
        )
    
    def test_create_video_analysis(self):
        """测试创建视频分析"""
        self.assertIsNotNone(self.video_analysis.id)
        self.assertEqual(self.video_analysis.resume, self.resume)
        self.assertEqual(self.video_analysis.status, VideoAnalysis.Status.PENDING)
    
    def test_default_status_pending(self):
        """测试默认状态为等待分析"""
        self.assertEqual(self.video_analysis.status, VideoAnalysis.Status.PENDING)
    
    def test_candidate_name_property(self):
        """测试从关联简历获取候选人姓名"""
        self.assertEqual(self.video_analysis.candidate_name, "张三")
    
    def test_position_applied_property(self):
        """测试从关联简历获取应聘岗位"""
        self.assertEqual(self.video_analysis.position_applied, "Python开发工程师")
    
    def test_set_analysis_result(self):
        """测试设置分析结果"""
        result = {
            "personality": {
                "neuroticism": 0.3,
                "extraversion": 0.7
            },
            "fraud_score": 0.1,
            "confidence_score": 0.85
        }
        self.video_analysis.set_analysis_result(result)
        
        self.assertEqual(self.video_analysis.analysis_result, result)
        self.assertEqual(self.video_analysis.status, VideoAnalysis.Status.COMPLETED)
    
    def test_mark_failed(self):
        """测试标记失败"""
        error_msg = "视频格式不支持"
        self.video_analysis.mark_failed(error_msg)
        
        self.assertEqual(self.video_analysis.status, VideoAnalysis.Status.FAILED)
        self.assertEqual(self.video_analysis.error_message, error_msg)
    
    def test_cascade_delete_on_resume(self):
        """测试删除简历时级联删除视频分析"""
        analysis_id = self.video_analysis.id
        self.resume.delete()
        
        # 视频分析应该被级联删除
        self.assertFalse(VideoAnalysis.objects.filter(id=analysis_id).exists())
    
    def test_str_representation(self):
        """测试字符串表示"""
        self.assertIn("张三", str(self.video_analysis))
        self.assertIn("面试视频1.mp4", str(self.video_analysis))
