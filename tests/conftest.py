"""
Pytest配置和测试数据。
"""
import pytest
from django.test import Client


@pytest.fixture
def api_client():
    """创建测试客户端。"""
    return Client()


@pytest.fixture
def sample_position_data():
    """测试用的样本岗位数据。"""
    return {
        "position": "Python开发工程师",
        "required_skills": ["Python", "Django", "MySQL"],
        "optional_skills": ["Redis", "Docker"],
        "min_experience": 2,
        "education": ["本科", "硕士"],
        "salary_range": [10000, 20000],
        "project_requirements": {
            "min_projects": 2,
            "team_lead_experience": True
        }
    }


@pytest.fixture
def sample_resume_data():
    """测试用的样本简历数据。"""
    return {
        "name": "张三简历.pdf",
        "content": """
姓名：张三
学历：本科
工作经验：3年
技术栈：Python, Django, MySQL, Redis
项目经验：
1. 电商后台系统开发
2. 数据分析平台建设
        """,
        "metadata": {
            "size": 1024,
            "type": "application/pdf"
        }
    }


@pytest.fixture
def screening_task(db):
    """创建筛选任务测试数据。"""
    from apps.resume_screening.models import ResumeScreeningTask
    
    return ResumeScreeningTask.objects.create(
        status='pending',
        progress=0,
        total_steps=1
    )


@pytest.fixture
def video_analysis(db):
    """创建视频分析测试数据。"""
    from apps.video_analysis.models import VideoAnalysis
    
    return VideoAnalysis.objects.create(
        video_name="test_video.mp4",
        candidate_name="测试候选人",
        position_applied="Python开发工程师",
        status='pending'
    )
