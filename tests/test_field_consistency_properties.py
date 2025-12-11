"""
前后端字段一致性属性测试。

验证后端模型/序列化器字段与前端TypeScript类型定义保持一致。

Feature: api-optimization, Property 9: 前后端字段一致性
Validates: Requirements 7.2
"""
import pytest
import re
import os
from pathlib import Path


# 前端类型定义文件路径
FRONTEND_TYPES_PATH = Path(__file__).parent.parent.parent / 'HRM2-Vue-Frontend_new' / 'src' / 'types' / 'index.ts'
FRONTEND_API_PATH = Path(__file__).parent.parent.parent / 'HRM2-Vue-Frontend_new' / 'src' / 'api' / 'index.ts'


def parse_typescript_interface(content: str, interface_name: str) -> set:
    """从TypeScript内容中解析接口字段名。"""
    # 匹配 export interface InterfaceName { ... }
    pattern = rf'export interface {interface_name}\s*(?:<[^>]+>)?\s*\{{([^}}]+)\}}'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return set()
    
    body = match.group(1)
    fields = set()
    
    # 匹配字段名（包括可选字段）
    field_pattern = r'^\s*(\w+)\??:'
    for line in body.split('\n'):
        field_match = re.match(field_pattern, line)
        if field_match:
            fields.add(field_match.group(1))
    
    return fields


def get_serializer_fields(serializer_class) -> set:
    """获取序列化器的字段名。"""
    if hasattr(serializer_class, 'Meta') and hasattr(serializer_class.Meta, 'fields'):
        return set(serializer_class.Meta.fields)
    return set()


def get_model_fields(model_class) -> set:
    """获取模型的字段名。"""
    return {f.name for f in model_class._meta.get_fields() if hasattr(f, 'name')}


# **Feature: api-optimization, Property 9: 前后端字段一致性**
class TestFrontendBackendFieldConsistency:
    """
    Property 9: 前后端字段一致性
    
    验证后端序列化器字段与前端TypeScript接口字段保持一致，
    确保字段命名遵循统一规范（snake_case）。
    
    Validates: Requirements 7.2
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """设置测试环境。"""
        if FRONTEND_TYPES_PATH.exists():
            self.types_content = FRONTEND_TYPES_PATH.read_text(encoding='utf-8')
        else:
            self.types_content = ""
        
        if FRONTEND_API_PATH.exists():
            self.api_content = FRONTEND_API_PATH.read_text(encoding='utf-8')
        else:
            self.api_content = ""
    
    def test_frontend_types_file_exists(self):
        """前端类型定义文件应存在。"""
        assert FRONTEND_TYPES_PATH.exists(), f"前端类型文件不存在: {FRONTEND_TYPES_PATH}"
    
    def test_frontend_api_file_exists(self):
        """前端API文件应存在。"""
        assert FRONTEND_API_PATH.exists(), f"前端API文件不存在: {FRONTEND_API_PATH}"
    
    def test_resume_data_fields_use_snake_case(self):
        """ResumeData接口字段应使用snake_case命名。"""
        fields = parse_typescript_interface(self.types_content, 'ResumeData')
        
        assert len(fields) > 0, "未找到ResumeData接口定义"
        
        # 验证字段使用snake_case
        for field in fields:
            # snake_case: 全小写，单词之间用下划线分隔
            assert field.islower() or '_' in field, \
                f"字段 '{field}' 不符合snake_case命名规范"
    
    def test_resume_data_no_alias_fields(self):
        """ResumeData接口不应包含别名字段。"""
        fields = parse_typescript_interface(self.types_content, 'ResumeData')
        
        # 验证不存在别名字段
        alias_fields = {'scores', 'summary'}  # 已弃用的别名
        found_aliases = fields & alias_fields
        
        assert len(found_aliases) == 0, \
            f"发现已弃用的别名字段: {found_aliases}，应使用 screening_score, screening_summary"
    
    def test_resume_data_score_fields_consistency(self):
        """验证评分字段命名一致性。"""
        fields = parse_typescript_interface(self.types_content, 'ResumeData')
        
        # 应该使用 screening_score 而非 scores
        assert 'screening_score' in fields, \
            "ResumeData应包含 screening_score 字段"
        assert 'scores' not in fields, \
            "ResumeData不应包含 scores 别名字段"
    
    def test_resume_data_summary_fields_consistency(self):
        """验证摘要字段命名一致性。"""
        fields = parse_typescript_interface(self.types_content, 'ResumeData')
        
        # 应该使用 screening_summary 而非 summary
        assert 'screening_summary' in fields, \
            "ResumeData应包含 screening_summary 字段"
        assert 'summary' not in fields, \
            "ResumeData不应包含 summary 别名字段"
    
    def test_resume_data_score_interface_fields_no_alias(self):
        """ResumeDataScore接口不应包含别名字段。"""
        fields = parse_typescript_interface(self.types_content, 'ResumeDataScore')
        
        if len(fields) > 0:
            # 应该使用 screening_score 而非 scores
            assert 'scores' not in fields, \
                "ResumeDataScore不应包含 scores 别名字段"
            assert 'summary' not in fields, \
                "ResumeDataScore不应包含 summary 别名字段"
    
    def test_screening_score_interface_exists(self):
        """ScreeningScore接口应存在。"""
        fields = parse_typescript_interface(self.types_content, 'ScreeningScore')
        
        assert len(fields) > 0, "未找到ScreeningScore接口定义"
        
        # 验证包含必要的评分字段
        expected_fields = {'comprehensive_score'}
        assert expected_fields.issubset(fields), \
            f"ScreeningScore缺少必要字段: {expected_fields - fields}"
    
    def test_api_response_interface_matches_backend(self):
        """ApiResponse接口应与后端响应格式一致。"""
        fields = parse_typescript_interface(self.types_content, 'ApiResponse')
        
        # 验证包含 code, message, data
        expected_fields = {'code', 'message', 'data'}
        assert expected_fields.issubset(fields), \
            f"ApiResponse缺少必要字段: {expected_fields - fields}"
    
    def test_paginated_response_interface_matches_backend(self):
        """PaginatedResponse接口应与后端分页格式一致。"""
        fields = parse_typescript_interface(self.types_content, 'PaginatedResponse')
        
        # 验证包含 items, total, page, page_size（后端 ApiResponse.paginated 格式）
        expected_fields = {'items', 'total', 'page', 'page_size'}
        assert expected_fields.issubset(fields), \
            f"PaginatedResponse缺少必要字段: {expected_fields - fields}"
        
        # 验证不包含旧格式字段
        old_fields = {'results', 'count', 'next', 'previous'}
        found_old = fields & old_fields
        assert len(found_old) == 0, \
            f"PaginatedResponse包含旧格式字段: {found_old}，应使用 items, total, page, page_size"


class TestBackendSerializerFieldConsistency:
    """
    验证后端序列化器字段命名规范。
    """
    
    def test_resume_data_serializer_fields(self):
        """ResumeDataSerializer应包含正确的字段。"""
        from apps.resume_screening.serializers import ResumeDataSerializer
        
        fields = get_serializer_fields(ResumeDataSerializer)
        
        # 验证包含核心字段
        expected_fields = {
            'id', 'created_at', 'candidate_name', 'position_title',
            'screening_score', 'screening_summary'
        }
        assert expected_fields.issubset(fields), \
            f"ResumeDataSerializer缺少字段: {expected_fields - fields}"
        
        # 验证不包含别名字段
        assert 'scores' not in fields, \
            "ResumeDataSerializer不应包含 scores 别名"
        assert 'summary' not in fields, \
            "ResumeDataSerializer不应包含 summary 别名"
    
    def test_resume_data_model_fields(self):
        """ResumeData模型应使用snake_case字段命名。"""
        from apps.resume_screening.models import ResumeData
        
        fields = get_model_fields(ResumeData)
        
        # 验证核心字段存在
        expected_fields = {'screening_score', 'screening_summary', 'candidate_name'}
        assert expected_fields.issubset(fields), \
            f"ResumeData模型缺少字段: {expected_fields - fields}"
    
    def test_library_resume_serializer_fields(self):
        """LibraryResumeSerializer应包含正确的字段（如果存在）。"""
        try:
            from apps.resume_library.serializers import ResumeLibrarySerializer
            
            fields = get_serializer_fields(ResumeLibrarySerializer)
            
            # 验证包含核心字段
            expected_fields = {'id', 'filename', 'candidate_name', 'is_screened'}
            assert expected_fields.issubset(fields), \
                f"ResumeLibrarySerializer缺少字段: {expected_fields - fields}"
        except ImportError:
            pytest.skip("ResumeLibrarySerializer不存在")
    
    def test_video_analysis_serializer_uses_snake_case(self):
        """视频分析相关字段应使用snake_case命名。"""
        from apps.video_analysis.models import VideoAnalysis
        
        fields = get_model_fields(VideoAnalysis)
        
        # 验证人格特质评分字段使用snake_case
        score_fields = {
            'fraud_score', 'neuroticism_score', 'extraversion_score',
            'openness_score', 'agreeableness_score', 'conscientiousness_score'
        }
        assert score_fields.issubset(fields), \
            f"VideoAnalysis缺少评分字段: {score_fields - fields}"


class TestFieldNamingConvention:
    """
    验证字段命名规范。
    """
    
    def test_frontend_interfaces_use_snake_case(self):
        """前端主要接口字段应使用snake_case命名。"""
        if not FRONTEND_TYPES_PATH.exists():
            pytest.skip("前端类型文件不存在")
        
        content = FRONTEND_TYPES_PATH.read_text(encoding='utf-8')
        
        # 检查主要接口
        interfaces_to_check = [
            'ResumeData', 'ResumeDataScore', 'ScreeningScore',
            'VideoAnalysis', 'PositionData'
        ]
        
        for interface_name in interfaces_to_check:
            fields = parse_typescript_interface(content, interface_name)
            if len(fields) == 0:
                continue
            
            for field in fields:
                # 允许全小写或snake_case
                is_valid = field.islower() or (
                    '_' in field and 
                    all(part.islower() or part.isdigit() for part in field.split('_'))
                )
                assert is_valid, \
                    f"接口 {interface_name} 的字段 '{field}' 不符合snake_case命名规范"
    
    def test_no_camel_case_in_api_fields(self):
        """API字段不应使用camelCase命名。"""
        if not FRONTEND_TYPES_PATH.exists():
            pytest.skip("前端类型文件不存在")
        
        content = FRONTEND_TYPES_PATH.read_text(encoding='utf-8')
        
        # 检查是否有camelCase字段（小写开头，中间有大写）
        camel_case_pattern = r'^\s*([a-z][a-zA-Z]*[A-Z][a-zA-Z]*)\??:'
        camel_case_fields = []
        
        for line in content.split('\n'):
            match = re.match(camel_case_pattern, line)
            if match:
                field = match.group(1)
                # 排除一些特殊情况
                if field not in ['createdAt', 'updatedAt']:  # 时间戳字段可能用camelCase
                    camel_case_fields.append(field)
        
        # 允许少量camelCase字段（向后兼容）
        assert len(camel_case_fields) <= 5, \
            f"发现过多camelCase字段: {camel_case_fields}，应使用snake_case"
