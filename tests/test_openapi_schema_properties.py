"""
OpenAPI Schema一致性属性测试。

验证OpenAPI Schema与实际URL实现的一致性。
Validates: Requirements 5.1
"""
import re
import json
import pytest
from pathlib import Path
from django.urls import get_resolver, URLPattern, URLResolver


def get_all_api_urls():
    """
    获取所有API端点URL。
    
    Returns:
        list: 包含 (pattern, name, view_class, http_methods) 元组的列表
    """
    resolver = get_resolver()
    urls = []
    
    def extract_urls(resolver, prefix=''):
        for pattern in resolver.url_patterns:
            if isinstance(pattern, URLPattern):
                full_pattern = prefix + str(pattern.pattern)
                view_class = pattern.callback
                view_name = getattr(view_class, '__name__', str(view_class))
                
                # 获取视图支持的HTTP方法
                http_methods = []
                if hasattr(view_class, 'view_class'):
                    # Class-based view
                    cls = view_class.view_class
                    for method in ['get', 'post', 'put', 'patch', 'delete']:
                        if hasattr(cls, method) or hasattr(cls, f'handle_{method}'):
                            http_methods.append(method.upper())
                
                urls.append((full_pattern, pattern.name, view_name, http_methods))
            elif isinstance(pattern, URLResolver):
                new_prefix = prefix + str(pattern.pattern)
                extract_urls(pattern, new_prefix)
    
    extract_urls(resolver)
    return urls


def get_api_endpoint_urls():
    """
    获取所有以 /api/ 开头的业务端点URL（排除文档路由）。
    
    Returns:
        list: API端点URL列表
    """
    all_urls = get_all_api_urls()
    api_urls = []
    
    # 排除的路径（非业务端点）
    excluded_patterns = [
        r'^api/$',           # 重定向
        r'^api/schema/',     # OpenAPI schema
        r'^api/docs/',       # Swagger UI
        r'^api/redoc/',      # ReDoc
        r'^admin/',          # Admin
        r'^__debug__/',      # Debug toolbar
    ]
    
    for pattern, name, view_name, methods in all_urls:
        # 跳过排除的路径
        if any(re.match(excluded, pattern) for excluded in excluded_patterns):
            continue
        # 只包含 /api/ 开头的路径
        if pattern.startswith('api/'):
            api_urls.append((pattern, name, view_name, methods))
    
    return api_urls


def load_openapi_schema():
    """
    加载OpenAPI Schema JSON文件。
    
    Returns:
        dict: OpenAPI Schema
    """
    schema_path = Path(__file__).parent.parent / 'Docs' / 'openapi.json'
    if not schema_path.exists():
        pytest.skip("OpenAPI schema file not found")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_django_pattern(pattern):
    """
    将Django URL模式转换为OpenAPI路径格式。
    
    例如: api/positions/<uuid:position_id>/ -> /api/positions/{position_id}/
    """
    # 添加前导斜杠
    if not pattern.startswith('/'):
        pattern = '/' + pattern
    
    # 转换参数格式: <type:name> -> {name}
    pattern = re.sub(r'<\w+:(\w+)>', r'{\1}', pattern)
    
    # 确保以斜杠结尾
    if not pattern.endswith('/'):
        pattern = pattern + '/'
    
    return pattern


def normalize_openapi_path(path):
    """
    规范化OpenAPI路径格式。
    """
    # 确保以斜杠结尾
    if not path.endswith('/'):
        path = path + '/'
    return path


# **Feature: api-optimization, Property 6: OpenAPI Schema与实现一致性**
class TestOpenAPISchemaConsistency:
    """
    Property 6: OpenAPI Schema与实现一致性
    
    对于任何注册的API端点，该端点应同时出现在OpenAPI Schema中。
    对于OpenAPI Schema中的任何路径，Django URL配置中应存在对应的路由。
    
    Validates: Requirements 5.1
    """
    
    def test_schema_file_exists(self):
        """OpenAPI Schema文件应存在。"""
        schema_path = Path(__file__).parent.parent / 'Docs' / 'openapi.json'
        assert schema_path.exists(), f"OpenAPI schema 文件不存在: {schema_path}"
    
    def test_schema_has_paths(self):
        """OpenAPI Schema应包含paths定义。"""
        schema = load_openapi_schema()
        assert 'paths' in schema, "OpenAPI schema 缺少 'paths' 字段"
        assert len(schema['paths']) > 0, "OpenAPI schema paths 为空"
    
    def test_schema_has_info(self):
        """OpenAPI Schema应包含基本信息。"""
        schema = load_openapi_schema()
        
        assert 'info' in schema, "OpenAPI schema 缺少 'info' 字段"
        info = schema['info']
        
        assert 'title' in info, "OpenAPI schema info 缺少 'title'"
        assert 'version' in info, "OpenAPI schema info 缺少 'version'"
    
    def test_all_django_urls_in_schema(self):
        """所有Django API端点应在OpenAPI Schema中存在。"""
        schema = load_openapi_schema()
        api_urls = get_api_endpoint_urls()
        
        schema_paths = set(schema.get('paths', {}).keys())
        
        missing_in_schema = []
        for pattern, name, view_name, methods in api_urls:
            normalized = normalize_django_pattern(pattern)
            
            if normalized not in schema_paths:
                missing_in_schema.append(f"{normalized} (Django: {pattern})")
        
        assert len(missing_in_schema) == 0, \
            f"以下Django端点未在OpenAPI Schema中定义:\n" + "\n".join(missing_in_schema)
    
    def test_all_schema_paths_in_django(self):
        """OpenAPI Schema中的所有路径应在Django URL配置中存在。"""
        schema = load_openapi_schema()
        api_urls = get_api_endpoint_urls()
        
        # 获取所有Django URL的规范化形式
        django_paths = set()
        for pattern, name, view_name, methods in api_urls:
            normalized = normalize_django_pattern(pattern)
            django_paths.add(normalized)
        
        schema_paths = schema.get('paths', {}).keys()
        
        missing_in_django = []
        for path in schema_paths:
            normalized = normalize_openapi_path(path)
            if normalized not in django_paths:
                missing_in_django.append(path)
        
        assert len(missing_in_django) == 0, \
            f"以下OpenAPI路径在Django URL配置中不存在:\n" + "\n".join(missing_in_django)
    
    def test_schema_paths_have_operations(self):
        """OpenAPI Schema中的每个路径应至少有一个HTTP操作定义。"""
        schema = load_openapi_schema()
        
        http_methods = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options'}
        
        paths_without_operations = []
        for path, operations in schema.get('paths', {}).items():
            defined_methods = set(operations.keys()) & http_methods
            if len(defined_methods) == 0:
                paths_without_operations.append(path)
        
        assert len(paths_without_operations) == 0, \
            f"以下路径缺少HTTP操作定义:\n" + "\n".join(paths_without_operations)
    
    def test_schema_operations_have_responses(self):
        """OpenAPI Schema中的每个操作应有响应定义。"""
        schema = load_openapi_schema()
        
        http_methods = {'get', 'post', 'put', 'patch', 'delete'}
        
        operations_without_responses = []
        for path, operations in schema.get('paths', {}).items():
            for method, operation in operations.items():
                if method not in http_methods:
                    continue
                if not isinstance(operation, dict):
                    continue
                if 'responses' not in operation:
                    operations_without_responses.append(f"{method.upper()} {path}")
        
        assert len(operations_without_responses) == 0, \
            f"以下操作缺少响应定义:\n" + "\n".join(operations_without_responses)


class TestOpenAPISchemaQuality:
    """
    OpenAPI Schema质量测试。
    
    验证Schema的完整性和质量。
    """
    
    def test_schema_version_is_valid(self):
        """OpenAPI Schema版本应有效。"""
        schema = load_openapi_schema()
        
        assert 'openapi' in schema, "OpenAPI schema 缺少版本号"
        version = schema['openapi']
        
        # 应该是 3.x.x 版本
        assert version.startswith('3.'), f"不支持的OpenAPI版本: {version}"
    
    def test_all_operations_have_operation_id(self):
        """所有操作应有operationId。"""
        schema = load_openapi_schema()
        
        http_methods = {'get', 'post', 'put', 'patch', 'delete'}
        
        missing_operation_id = []
        for path, operations in schema.get('paths', {}).items():
            for method, operation in operations.items():
                if method not in http_methods:
                    continue
                if not isinstance(operation, dict):
                    continue
                if 'operationId' not in operation:
                    missing_operation_id.append(f"{method.upper()} {path}")
        
        assert len(missing_operation_id) == 0, \
            f"以下操作缺少operationId:\n" + "\n".join(missing_operation_id)
    
    def test_all_operations_have_tags(self):
        """所有操作应有标签分组。"""
        schema = load_openapi_schema()
        
        http_methods = {'get', 'post', 'put', 'patch', 'delete'}
        
        missing_tags = []
        for path, operations in schema.get('paths', {}).items():
            for method, operation in operations.items():
                if method not in http_methods:
                    continue
                if not isinstance(operation, dict):
                    continue
                tags = operation.get('tags', [])
                if len(tags) == 0:
                    missing_tags.append(f"{method.upper()} {path}")
        
        assert len(missing_tags) == 0, \
            f"以下操作缺少标签:\n" + "\n".join(missing_tags)
    
    def test_path_parameters_defined(self):
        """路径参数应有定义。"""
        schema = load_openapi_schema()
        
        issues = []
        for path, operations in schema.get('paths', {}).items():
            # 提取路径中的参数名
            path_params = re.findall(r'\{(\w+)\}', path)
            
            if not path_params:
                continue
            
            # 检查每个操作是否定义了这些参数
            http_methods = {'get', 'post', 'put', 'patch', 'delete'}
            for method, operation in operations.items():
                if method not in http_methods:
                    continue
                if not isinstance(operation, dict):
                    continue
                
                # 获取已定义的参数
                parameters = operation.get('parameters', [])
                defined_params = {
                    p.get('name') for p in parameters 
                    if p.get('in') == 'path'
                }
                
                # 检查是否所有路径参数都已定义
                missing = set(path_params) - defined_params
                if missing:
                    issues.append(f"{method.upper()} {path}: 缺少参数定义 {missing}")
        
        assert len(issues) == 0, \
            f"以下操作缺少路径参数定义:\n" + "\n".join(issues)
    
    def test_schema_endpoint_count_matches(self):
        """Schema中的端点数量应与Django配置大致匹配。"""
        schema = load_openapi_schema()
        api_urls = get_api_endpoint_urls()
        
        schema_paths = len(schema.get('paths', {}))
        django_paths = len(api_urls)
        
        # 允许一定的差异（因为某些视图可能无法自动推断）
        diff = abs(schema_paths - django_paths)
        tolerance = max(5, django_paths * 0.1)  # 10%容差或5个端点
        
        assert diff <= tolerance, \
            f"Schema端点数({schema_paths})与Django端点数({django_paths})差异过大"


class TestOpenAPIDocumentation:
    """
    OpenAPI文档完整性测试。
    
    验证Markdown文档与Schema的同步状态。
    """
    
    def test_markdown_doc_exists(self):
        """API参考文档应存在。"""
        doc_path = Path(__file__).parent.parent / 'Docs' / 'API参考文档.md'
        assert doc_path.exists(), f"API参考文档不存在: {doc_path}"
    
    def test_markdown_doc_not_empty(self):
        """API参考文档应有内容。"""
        doc_path = Path(__file__).parent.parent / 'Docs' / 'API参考文档.md'
        
        if not doc_path.exists():
            pytest.skip("API参考文档不存在")
        
        content = doc_path.read_text(encoding='utf-8')
        assert len(content) > 1000, "API参考文档内容太少"
    
    def test_markdown_doc_has_expected_sections(self):
        """API参考文档应包含预期的章节。"""
        doc_path = Path(__file__).parent.parent / 'Docs' / 'API参考文档.md'
        
        if not doc_path.exists():
            pytest.skip("API参考文档不存在")
        
        content = doc_path.read_text(encoding='utf-8')
        
        expected_sections = [
            '概览',
            '目录',
            '快速参考',
            '接口详情',
        ]
        
        for section in expected_sections:
            assert section in content, f"API参考文档缺少 '{section}' 章节"
    
    def test_markdown_doc_has_new_api_prefix(self):
        """API参考文档应使用新的 /api/ 前缀路径。"""
        doc_path = Path(__file__).parent.parent / 'Docs' / 'API参考文档.md'
        
        if not doc_path.exists():
            pytest.skip("API参考文档不存在")
        
        content = doc_path.read_text(encoding='utf-8')
        
        # 检查是否包含新路径格式
        assert '/api/positions/' in content, "文档缺少 /api/positions/ 路径"
        assert '/api/library/' in content, "文档缺少 /api/library/ 路径"
        assert '/api/screening/' in content, "文档缺少 /api/screening/ 路径"
        
        # 检查是否不包含旧路径格式
        old_patterns = [
            '/position-settings/',
            '/resume-screening/',
            '/video-analysis/',
            '/final-recommend/',
            '/interview-assist/',
        ]
        
        for old_pattern in old_patterns:
            assert old_pattern not in content, f"文档仍包含旧路径格式: {old_pattern}"
