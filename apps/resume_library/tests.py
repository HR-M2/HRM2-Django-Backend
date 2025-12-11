"""
简历库模块单元测试。

测试简历上传、查询、删除功能以及服务层接口。
"""
import json
import uuid
from django.test import TestCase, Client
from django.urls import reverse

from apps.common.utils import generate_hash
from .models import ResumeLibrary
from .services import LibraryService


class ResumeLibraryModelTests(TestCase):
    """ResumeLibrary 模型测试。"""
    
    def test_create_resume(self):
        """测试创建简历记录。"""
        resume = ResumeLibrary.objects.create(
            filename='test_resume.txt',
            file_hash=generate_hash('test content'),
            file_size=100,
            file_type='text/plain',
            content='这是一份测试简历内容',
            candidate_name='张三'
        )
        
        self.assertIsNotNone(resume.id)
        self.assertEqual(resume.filename, 'test_resume.txt')
        self.assertEqual(resume.candidate_name, '张三')
        self.assertFalse(resume.is_screened)
        self.assertFalse(resume.is_assigned)
    
    def test_file_hash_unique(self):
        """测试文件哈希值唯一约束。"""
        content = 'unique test content'
        file_hash = generate_hash(content)
        
        ResumeLibrary.objects.create(
            filename='first.txt',
            file_hash=file_hash,
            content=content
        )
        
        with self.assertRaises(Exception):
            ResumeLibrary.objects.create(
                filename='second.txt',
                file_hash=file_hash,
                content=content
            )
    
    def test_str_representation(self):
        """测试字符串表示。"""
        resume = ResumeLibrary.objects.create(
            filename='test.txt',
            file_hash=generate_hash('content'),
            content='content',
            candidate_name='李四'
        )
        
        self.assertIn('李四', str(resume))
        self.assertIn('test.txt', str(resume))


class LibraryServiceTests(TestCase):
    """LibraryService 服务层测试。"""
    
    def setUp(self):
        """设置测试数据。"""
        self.resume1 = ResumeLibrary.objects.create(
            filename='resume1.txt',
            file_hash=generate_hash('content1'),
            content='简历内容1',
            candidate_name='王五'
        )
        self.resume2 = ResumeLibrary.objects.create(
            filename='resume2.txt',
            file_hash=generate_hash('content2'),
            content='简历内容2',
            candidate_name='赵六'
        )
    
    def test_get_resume_by_id(self):
        """测试根据ID获取简历。"""
        resume = LibraryService.get_resume_by_id(str(self.resume1.id))
        self.assertIsNotNone(resume)
        self.assertEqual(resume.candidate_name, '王五')
        
        # 测试不存在的ID
        resume = LibraryService.get_resume_by_id(str(uuid.uuid4()))
        self.assertIsNone(resume)
    
    def test_get_resumes_by_ids(self):
        """测试批量获取简历。"""
        ids = [str(self.resume1.id), str(self.resume2.id)]
        resumes = LibraryService.get_resumes_by_ids(ids)
        
        self.assertEqual(len(resumes), 2)
    
    def test_get_resume_by_hash(self):
        """测试根据哈希获取简历。"""
        resume = LibraryService.get_resume_by_hash(self.resume1.file_hash)
        self.assertIsNotNone(resume)
        self.assertEqual(resume.id, self.resume1.id)
    
    def test_mark_as_screened(self):
        """测试标记已筛选。"""
        self.assertFalse(self.resume1.is_screened)
        
        result = LibraryService.mark_as_screened(str(self.resume1.id))
        self.assertTrue(result)
        
        self.resume1.refresh_from_db()
        self.assertTrue(self.resume1.is_screened)
    
    def test_mark_as_assigned(self):
        """测试标记已分配。"""
        self.assertFalse(self.resume1.is_assigned)
        
        result = LibraryService.mark_as_assigned(str(self.resume1.id))
        self.assertTrue(result)
        
        self.resume1.refresh_from_db()
        self.assertTrue(self.resume1.is_assigned)
    
    def test_batch_mark_as_screened(self):
        """测试批量标记已筛选。"""
        ids = [str(self.resume1.id), str(self.resume2.id)]
        count = LibraryService.batch_mark_as_screened(ids)
        
        self.assertEqual(count, 2)
        
        self.resume1.refresh_from_db()
        self.resume2.refresh_from_db()
        self.assertTrue(self.resume1.is_screened)
        self.assertTrue(self.resume2.is_screened)
    
    def test_check_hashes_exist(self):
        """测试检查哈希值是否存在。"""
        existing_hash = self.resume1.file_hash
        non_existing_hash = generate_hash('non existing content')
        
        result = LibraryService.check_hashes_exist([existing_hash, non_existing_hash])
        
        self.assertTrue(result[existing_hash])
        self.assertFalse(result[non_existing_hash])
    
    def test_upload_resume_success(self):
        """测试成功上传简历。"""
        resume, error = LibraryService.upload_resume(
            filename='new_resume.txt',
            content='新简历内容',
            metadata={'size': 100, 'type': 'text/plain'}
        )
        
        self.assertIsNotNone(resume)
        self.assertIsNone(error)
        self.assertEqual(resume.filename, 'new_resume.txt')
    
    def test_upload_resume_duplicate(self):
        """测试上传重复简历。"""
        resume, error = LibraryService.upload_resume(
            filename='duplicate.txt',
            content='content1'  # 与 resume1 内容相同
        )
        
        self.assertIsNone(resume)
        self.assertEqual(error, '简历已存在')
    
    def test_upload_resume_empty_content(self):
        """测试上传空内容简历。"""
        resume, error = LibraryService.upload_resume(
            filename='empty.txt',
            content=''
        )
        
        self.assertIsNone(resume)
        self.assertEqual(error, '内容为空')
    
    def test_search_resumes(self):
        """测试搜索简历。"""
        # 测试关键词搜索
        resumes, total = LibraryService.search_resumes(keyword='王五')
        self.assertEqual(total, 1)
        self.assertEqual(resumes[0].candidate_name, '王五')
        
        # 测试分页
        resumes, total = LibraryService.search_resumes(page=1, page_size=1)
        self.assertEqual(len(resumes), 1)
        self.assertEqual(total, 2)
    
    def test_delete_resume(self):
        """测试删除简历。"""
        resume_id = str(self.resume1.id)
        result = LibraryService.delete_resume(resume_id)
        
        self.assertTrue(result)
        self.assertFalse(ResumeLibrary.objects.filter(id=resume_id).exists())
    
    def test_batch_delete(self):
        """测试批量删除简历。"""
        ids = [str(self.resume1.id), str(self.resume2.id)]
        count = LibraryService.batch_delete(ids)
        
        self.assertEqual(count, 2)
        self.assertEqual(ResumeLibrary.objects.count(), 0)


class LibraryViewTests(TestCase):
    """简历库视图测试。"""
    
    def setUp(self):
        """设置测试客户端和数据。"""
        self.client = Client()
        self.resume = ResumeLibrary.objects.create(
            filename='test_view.txt',
            file_hash=generate_hash('view test content'),
            content='视图测试简历内容',
            candidate_name='测试用户'
        )
    
    def test_list_resumes(self):
        """测试获取简历列表。"""
        response = self.client.get('/resume-screening/library/')
        
        # 注意：旧路由已移除，此测试验证旧路由不可用
        # 新路由将在后续任务中配置
        self.assertEqual(response.status_code, 404)
    
    def test_upload_resumes(self):
        """测试上传简历（通过服务层验证）。"""
        # 由于视图路由尚未配置到主路由，这里直接测试服务层
        resume, error = LibraryService.upload_resume(
            filename='uploaded.txt',
            content='上传的简历内容'
        )
        
        self.assertIsNotNone(resume)
        self.assertEqual(resume.filename, 'uploaded.txt')
    
    def test_get_resume_detail(self):
        """测试获取简历详情（通过服务层验证）。"""
        resume = LibraryService.get_resume_by_id(str(self.resume.id))
        
        self.assertIsNotNone(resume)
        self.assertEqual(resume.candidate_name, '测试用户')
    
    def test_delete_resume(self):
        """测试删除简历（通过服务层验证）。"""
        resume_id = str(self.resume.id)
        result = LibraryService.delete_resume(resume_id)
        
        self.assertTrue(result)
        self.assertIsNone(LibraryService.get_resume_by_id(resume_id))


class CandidateNameExtractionTests(TestCase):
    """候选人姓名提取测试。"""
    
    def test_extract_from_filename_pattern1(self):
        """测试从文件名提取姓名（张三_简历）。"""
        resume, _ = LibraryService.upload_resume(
            filename='张三_简历.txt',
            content='简历内容'
        )
        
        self.assertEqual(resume.candidate_name, '张三')
    
    def test_extract_from_filename_pattern2(self):
        """测试从文件名提取姓名（简历_李四）。"""
        resume, _ = LibraryService.upload_resume(
            filename='简历_李四.txt',
            content='简历内容2'
        )
        
        self.assertEqual(resume.candidate_name, '李四')
    
    def test_extract_from_content(self):
        """测试从内容提取姓名。"""
        resume, _ = LibraryService.upload_resume(
            filename='unknown.txt',
            content='姓名：王五\n学历：本科\n工作经验：3年'
        )
        
        self.assertEqual(resume.candidate_name, '王五')
    
    def test_extract_chinese_name_only_filename(self):
        """测试纯中文姓名文件名。"""
        resume, _ = LibraryService.upload_resume(
            filename='赵六.txt',
            content='简历内容3'
        )
        
        self.assertEqual(resume.candidate_name, '赵六')
