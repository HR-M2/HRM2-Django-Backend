"""
前后端数据格式一致性测试

Property 11: 数据格式一致性
- 验证后端API返回的字段命名符合规范
- 验证分页响应格式一致
- 防止后续修改引入不一致

Requirements: 7.2, 3.1, 8.3
"""
import ast
import os
import re
import pytest
from pathlib import Path


class TestFieldNamingConsistency:
    """测试后端字段命名一致性"""
    
    @pytest.fixture
    def backend_views_dir(self):
        """后端视图目录"""
        return Path(__file__).parent.parent / "apps"
    
    def get_python_files(self, directory: Path) -> list:
        """获取目录下所有 Python 文件"""
        return list(directory.rglob("*.py"))
    
    def test_no_scores_field_in_responses(self, backend_views_dir):
        """
        验证视图返回中不使用 'scores' 作为返回字段名（应使用 screening_score）
        
        检查规则：
        - 查找 "scores": 模式作为返回字段
        - 排除注释和变量赋值
        """
        violations = []
        
        view_files = [
            f for f in self.get_python_files(backend_views_dir)
            if 'views' in str(f) or f.name == 'views.py'
        ]
        
        # 检查模式：在响应字典中使用 "scores" 作为键（排除变量声明如 scores = {}）
        pattern = re.compile(r'["\']scores["\']:\s*[^=]')
        
        for file_path in view_files:
            content = file_path.read_text(encoding='utf-8')
            matches = pattern.finditer(content)
            for match in matches:
                line_start = content.rfind('\n', 0, match.start()) + 1
                line = content[line_start:content.find('\n', match.end())]
                # 排除注释行和变量赋值行
                if not line.strip().startswith('#') and 'scores = ' not in line:
                    violations.append(f"{file_path.name}: 使用了 'scores' 字段")
        
        assert not violations, (
            f"发现使用非规范字段名 'scores' (应使用 'screening_score'):\n"
            + "\n".join(violations)
        )
    
    def test_no_summary_mapping_screening_summary(self, backend_views_dir):
        """
        验证视图返回中不使用 'summary' 字段来映射 .screening_summary
        （应直接使用 'screening_summary' 作为字段名）
        
        合法的 'summary' 用法：
        - video_analysis 的 summary 字段（video.summary 或 .video_analysis.summary）
        - 分组摘要信息（"summary": { ... }）
        """
        violations = []
        
        view_files = [
            f for f in self.get_python_files(backend_views_dir)
            if 'views' in str(f) or f.name == 'views.py'
        ]
        
        # 检查模式：使用 "summary" 映射 .screening_summary（这是不规范的）
        pattern = re.compile(r'["\']summary["\']:\s*\w+\.screening_summary')
        
        for file_path in view_files:
            content = file_path.read_text(encoding='utf-8')
            matches = pattern.finditer(content)
            for match in matches:
                violations.append(
                    f"{file_path.name}: 使用 'summary' 映射 screening_summary"
                )
        
        assert not violations, (
            f"发现使用非规范字段名 'summary' 映射 screening_summary:\n"
            + "\n".join(violations)
        )
    
    def test_video_api_uses_id_not_video_id(self, backend_views_dir):
        """
        验证视频API返回中使用 'id' 而非 'video_id'
        """
        violations = []
        
        video_views_file = backend_views_dir / "video_analysis" / "views.py"
        if video_views_file.exists():
            content = video_views_file.read_text(encoding='utf-8')
            
            # 检查是否使用了 video_id 作为返回字段
            pattern = re.compile(r'["\']video_id["\']:\s*str\(')
            matches = pattern.finditer(content)
            
            for match in matches:
                line_start = content.rfind('\n', 0, match.start()) + 1
                line = content[line_start:content.find('\n', match.end())]
                if not line.strip().startswith('#'):
                    violations.append(f"video_analysis/views.py: {line.strip()}")
        
        assert not violations, (
            f"视频API应使用 'id' 而非 'video_id':\n"
            + "\n".join(violations)
        )


class TestPaginatedResponseFormat:
    """测试分页响应格式一致性"""
    
    def test_paginated_response_uses_items(self):
        """验证 ApiResponse.paginated() 使用 'items' 字段"""
        response_file = Path(__file__).parent.parent / "apps" / "common" / "response.py"
        content = response_file.read_text(encoding='utf-8')
        
        # 检查 paginated 方法是否使用 items 字段
        assert '"items"' in content or "'items'" in content, (
            "ApiResponse.paginated() 应使用 'items' 字段作为列表容器"
        )
    
    def test_paginated_response_structure(self):
        """验证分页响应包含必要字段"""
        response_file = Path(__file__).parent.parent / "apps" / "common" / "response.py"
        content = response_file.read_text(encoding='utf-8')
        
        required_fields = ['items', 'total', 'page', 'page_size']
        for field in required_fields:
            assert f'"{field}"' in content or f"'{field}'" in content, (
                f"ApiResponse.paginated() 应包含 '{field}' 字段"
            )


class TestFrontendBackendFieldAlignment:
    """测试前后端字段对齐"""
    
    @pytest.fixture
    def frontend_types_file(self):
        """前端类型定义文件"""
        return Path(__file__).parent.parent.parent / "HRM2-Vue-Frontend_new" / "src" / "types" / "index.ts"
    
    def test_resume_data_fields_match(self, frontend_types_file):
        """验证 ResumeData 类型的关键字段与后端一致"""
        if not frontend_types_file.exists():
            pytest.skip("前端类型文件不存在")
        
        content = frontend_types_file.read_text(encoding='utf-8')
        
        # 检查使用规范字段名
        assert 'screening_score' in content, "前端应使用 screening_score 字段"
        assert 'screening_summary' in content, "前端应使用 screening_summary 字段"
        
        # 确保没有使用旧的字段别名定义
        # 如果类型定义中同时有 scores 和 screening_score 作为同一数据的别名，则不符合规范
        # 这里简单检查是否在 ResumeData 接口中存在规范字段
    
    def test_video_analysis_uses_id(self, frontend_types_file):
        """验证 VideoAnalysis 类型使用 'id' 而非 'video_id'"""
        if not frontend_types_file.exists():
            pytest.skip("前端类型文件不存在")
        
        content = frontend_types_file.read_text(encoding='utf-8')
        
        # 在 VideoAnalysis 接口中应该使用 id
        # 查找 VideoAnalysis 接口定义
        video_pattern = re.compile(
            r'interface\s+VideoAnalysis\s*\{[^}]+\}',
            re.DOTALL
        )
        match = video_pattern.search(content)
        
        if match:
            video_interface = match.group()
            assert 'id:' in video_interface or 'id?:' in video_interface, (
                "VideoAnalysis 接口应包含 'id' 字段"
            )
            assert 'video_id' not in video_interface, (
                "VideoAnalysis 接口不应使用 'video_id'（应使用 'id'）"
            )
    
    def test_paginated_response_type_matches_backend(self, frontend_types_file):
        """验证前端 PaginatedResponse 类型与后端格式匹配"""
        if not frontend_types_file.exists():
            pytest.skip("前端类型文件不存在")
        
        content = frontend_types_file.read_text(encoding='utf-8')
        
        # 检查 PaginatedResponse 包含 items 字段
        paginated_pattern = re.compile(
            r'interface\s+PaginatedResponse[^{]*\{[^}]+\}',
            re.DOTALL
        )
        match = paginated_pattern.search(content)
        
        if match:
            paginated_interface = match.group()
            assert 'items:' in paginated_interface, (
                "PaginatedResponse 接口应包含 'items' 字段"
            )


class TestDataFormatRegressionPrevention:
    """防止数据格式回归的测试"""
    
    @pytest.fixture
    def backend_apps_dir(self):
        return Path(__file__).parent.parent / "apps"
    
    def test_resume_data_detail_view_uses_correct_fields(self, backend_apps_dir):
        """验证简历数据详情视图使用正确的字段名"""
        resume_data_view = backend_apps_dir / "resume_screening" / "views" / "resume_data.py"
        if not resume_data_view.exists():
            pytest.skip("简历数据视图文件不存在")
        
        content = resume_data_view.read_text(encoding='utf-8')
        
        # ResumeDataDetailView 应使用 screening_score 和 screening_summary
        if 'ResumeDataDetailView' in content or 'handle_get' in content:
            # 检查返回数据中使用正确字段
            assert '"screening_score"' in content or "'screening_score'" in content, (
                "ResumeDataDetailView 应返回 'screening_score' 字段"
            )
            assert '"screening_summary"' in content or "'screening_summary'" in content, (
                "ResumeDataDetailView 应返回 'screening_summary' 字段"
            )
    
    def test_video_analysis_list_view_uses_id(self, backend_apps_dir):
        """验证视频分析列表视图使用 'id' 字段"""
        video_views = backend_apps_dir / "video_analysis" / "views.py"
        if not video_views.exists():
            pytest.skip("视频分析视图文件不存在")
        
        content = video_views.read_text(encoding='utf-8')
        
        # 检查列表构建中使用 id 而非 video_id
        # 在 for video in items 循环中应该使用 "id"
        list_view_section = content.split('class VideoAnalysisListView')[-1] if 'VideoAnalysisListView' in content else content
        
        # 简单检查：在视图代码中 "id" 出现的次数应该大于 "video_id"
        id_count = list_view_section.count('"id"')
        video_id_count = list_view_section.count('"video_id"')
        
        assert video_id_count == 0, (
            f"VideoAnalysisListView 不应使用 'video_id'，应使用 'id'"
        )
