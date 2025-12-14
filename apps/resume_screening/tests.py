"""
筛选任务模型单元测试
"""
from django.test import TestCase
from apps.resume_screening.models import ScreeningTask
from apps.position_settings.models import Position


class ScreeningTaskModelTest(TestCase):
    """ScreeningTask 模型测试"""
    
    def setUp(self):
        """测试前创建测试数据"""
        self.position = Position.objects.create(
            title="Python开发工程师",
            department="技术部"
        )
        self.task = ScreeningTask.objects.create(
            position=self.position,
            total_count=10
        )
    
    def test_create_screening_task(self):
        """测试创建筛选任务"""
        self.assertIsNotNone(self.task.id)
        self.assertEqual(self.task.position, self.position)
        self.assertEqual(self.task.status, ScreeningTask.Status.PENDING)
    
    def test_default_status_pending(self):
        """测试默认状态为等待中"""
        self.assertEqual(self.task.status, ScreeningTask.Status.PENDING)
    
    def test_update_progress(self):
        """测试更新进度"""
        self.task.update_progress(3, 10)
        self.assertEqual(self.task.processed_count, 3)
        self.assertEqual(self.task.progress, 30)
        
        self.task.update_progress(7)
        self.assertEqual(self.task.processed_count, 7)
        self.assertEqual(self.task.progress, 70)
    
    def test_mark_completed(self):
        """测试标记完成"""
        self.task.mark_completed()
        self.assertEqual(self.task.status, ScreeningTask.Status.COMPLETED)
        self.assertEqual(self.task.progress, 100)
    
    def test_mark_failed(self):
        """测试标记失败"""
        error_msg = "处理出错: 网络超时"
        self.task.mark_failed(error_msg)
        self.assertEqual(self.task.status, ScreeningTask.Status.FAILED)
        self.assertEqual(self.task.error_message, error_msg)
    
    def test_str_representation(self):
        """测试字符串表示"""
        self.assertIn("Python开发工程师", str(self.task))
    
    def test_cascade_delete_on_position(self):
        """测试删除岗位时级联删除任务"""
        task_id = self.task.id
        self.position.delete()
        
        # 任务应该被级联删除
        self.assertFalse(ScreeningTask.objects.filter(id=task_id).exists())
    
    def test_progress_calculation(self):
        """测试进度百分比计算"""
        self.task.update_progress(5, 20)
        self.assertEqual(self.task.progress, 25)
        
        self.task.update_progress(20, 20)
        self.assertEqual(self.task.progress, 100)
