"""
API URL路径属性测试。

验证API路径规范的一致性。
"""
import re
import pytest
from django.urls import get_resolver, URLPattern, URLResolver


def get_all_api_urls():
    """
    获取所有API端点URL。
    
    Returns:
        list: 包含 (pattern, name, view_name) 元组的列表
    """
    resolver = get_resolver()
    urls = []
    
    def extract_urls(resolver, prefix=''):
        for pattern in resolver.url_patterns:
            if isinstance(pattern, URLPattern):
                full_pattern = prefix + str(pattern.pattern)
                view_name = getattr(pattern.callback, '__name__', str(pattern.callback))
                urls.append((full_pattern, pattern.name, view_name))
            elif isinstance(pattern, URLResolver):
                namespace = pattern.namespace or ''
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
    
    for pattern, name, view_name in all_urls:
        # 跳过排除的路径
        if any(re.match(excluded, pattern) for excluded in excluded_patterns):
            continue
        # 只包含 /api/ 开头的路径
        if pattern.startswith('api/'):
            api_urls.append((pattern, name, view_name))
    
    return api_urls


# **Feature: api-optimization, Property 1: API路径前缀一致性**
class TestApiPrefixConsistency:
    """
    Property 1: API路径前缀一致性
    
    对于任何注册的API端点URL，该URL路径应以 /api/ 开头（排除admin和静态文件路径）。
    
    Validates: Requirements 1.1
    """
    
    def test_all_business_apis_have_api_prefix(self):
        """所有业务API端点应以 /api/ 开头。"""
        all_urls = get_all_api_urls()
        
        # 定义业务模块的URL前缀（与主路由中的路径匹配）
        business_prefixes = [
            'positions/',   # 岗位管理
            'library/',     # 简历库
            'screening/',   # 简历筛选
            'videos/',      # 视频分析
            'recommend/',   # 最终推荐
            'interviews/',  # 面试辅助
        ]
        
        violations = []
        for pattern, name, view_name in all_urls:
            # 跳过 admin 路径
            if pattern.startswith('admin/'):
                continue
            # 跳过 debug 路径
            if pattern.startswith('__debug__/'):
                continue
            # 跳过媒体和静态文件路径
            if pattern.startswith('media/') or pattern.startswith('static/'):
                continue
            
            # 检查是否是业务模块的URL（以模块前缀开头但没有 api/ 前缀）
            for prefix in business_prefixes:
                if pattern.startswith(prefix) and not pattern.startswith('api/'):
                    violations.append(f"{pattern} (should start with 'api/')")
        
        assert len(violations) == 0, f"以下URL缺少 /api/ 前缀:\n" + "\n".join(violations)
    
    def test_api_endpoints_exist(self):
        """验证所有业务API端点都已注册。"""
        api_urls = get_api_endpoint_urls()
        
        # 验证各模块至少有一个端点
        expected_prefixes = [
            'api/positions/',
            'api/library/',
            'api/screening/',
            'api/videos/',
            'api/recommend/',
            'api/interviews/',
        ]
        
        patterns = [url[0] for url in api_urls]
        
        for prefix in expected_prefixes:
            matching = [p for p in patterns if p.startswith(prefix)]
            assert len(matching) > 0, f"未找到以 {prefix} 开头的API端点"


# **Feature: api-optimization, Property 2: 无冗余路径**
class TestNoRedundantPaths:
    """
    Property 2: 无冗余路径
    
    对于任何两个不同的URL模式，如果它们指向同一个视图类，
    则它们应具有不同的HTTP方法或不同的用途（如列表vs详情）。
    
    Validates: Requirements 1.4
    """
    
    def test_no_duplicate_list_endpoints(self):
        """不应存在冗余的列表端点（如同时存在 / 和 /list/）。"""
        api_urls = get_api_endpoint_urls()
        
        # 检查每个模块是否同时有 '' 和 'list/' 指向同一视图
        violations = []
        
        # 按模块分组
        modules = {}
        for pattern, name, view_name in api_urls:
            # 提取模块前缀 (如 api/positions/)
            parts = pattern.split('/')
            if len(parts) >= 2:
                module = f"api/{parts[1]}/"
                if module not in modules:
                    modules[module] = []
                modules[module].append((pattern, name, view_name))
        
        for module, urls in modules.items():
            # 检查是否同时存在根路径和 list/ 路径
            root_views = [(p, v) for p, n, v in urls if p == module or p == module.rstrip('/')]
            list_views = [(p, v) for p, n, v in urls if p == f"{module}list/"]
            
            for root_pattern, root_view in root_views:
                for list_pattern, list_view in list_views:
                    if root_view == list_view:
                        violations.append(
                            f"冗余路径: '{root_pattern}' 和 '{list_pattern}' 指向同一视图 '{root_view}'"
                        )
        
        assert len(violations) == 0, "发现冗余路径:\n" + "\n".join(violations)
    
    def test_removed_legacy_paths(self):
        """验证旧版冗余路径已被移除。"""
        api_urls = get_api_endpoint_urls()
        patterns = [url[0] for url in api_urls]
        
        # 应该被移除的旧路径模式
        legacy_patterns = [
            r'position-settings/',      # 旧前缀
            r'resume-screening/',       # 旧前缀
            r'video-analysis/',         # 旧前缀
            r'final-recommend/',        # 旧前缀
            r'interview-assist/',       # 旧前缀
            r'.*/list/$',               # 冗余的 list 路径
            r'.*/positions/positions/', # 重复的 positions 前缀
        ]
        
        violations = []
        for pattern in patterns:
            for legacy in legacy_patterns:
                if re.match(legacy, pattern):
                    violations.append(f"发现旧版路径: {pattern}")
        
        assert len(violations) == 0, "以下旧版路径应被移除:\n" + "\n".join(violations)


# **Feature: api-optimization, Property 10: URL路径命名规范**
class TestUrlPathNamingConvention:
    """
    Property 10: URL路径命名规范
    
    对于任何API端点的URL路径段，该路径段应符合kebab-case命名规范
    （小写字母和连字符）。
    
    Validates: Requirements 7.4
    """
    
    def test_all_path_segments_use_kebab_case(self):
        """所有路径段应使用kebab-case命名。"""
        api_urls = get_api_endpoint_urls()
        
        # kebab-case 模式: 小写字母、数字、连字符
        # 排除 UUID 占位符 和 特殊标记
        kebab_case_pattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
        
        violations = []
        for pattern, name, view_name in api_urls:
            # 分割路径段
            segments = pattern.strip('/').split('/')
            
            for segment in segments:
                # 跳过空段
                if not segment:
                    continue
                # 跳过 UUID 参数 (如 <uuid:id>)
                if segment.startswith('<') and segment.endswith('>'):
                    continue
                # 跳过纯数字段
                if segment.isdigit():
                    continue
                
                # 检查是否符合 kebab-case
                if not kebab_case_pattern.match(segment):
                    violations.append(f"路径 '{pattern}' 中的段 '{segment}' 不符合 kebab-case 规范")
        
        assert len(violations) == 0, "发现不符合 kebab-case 的路径段:\n" + "\n".join(violations)
    
    def test_no_underscores_in_paths(self):
        """路径中不应包含下划线（应使用连字符）。"""
        api_urls = get_api_endpoint_urls()
        
        violations = []
        for pattern, name, view_name in api_urls:
            # 移除参数占位符后检查
            cleaned_pattern = re.sub(r'<[^>]+>', '', pattern)
            if '_' in cleaned_pattern:
                violations.append(f"路径 '{pattern}' 包含下划线")
        
        assert len(violations) == 0, "以下路径包含下划线:\n" + "\n".join(violations)
    
    def test_no_camelcase_in_paths(self):
        """路径中不应使用驼峰命名。"""
        api_urls = get_api_endpoint_urls()
        
        # 驼峰模式: 小写字母后跟大写字母
        camel_case_pattern = re.compile(r'[a-z][A-Z]')
        
        violations = []
        for pattern, name, view_name in api_urls:
            # 移除参数占位符后检查
            cleaned_pattern = re.sub(r'<[^>]+>', '', pattern)
            if camel_case_pattern.search(cleaned_pattern):
                violations.append(f"路径 '{pattern}' 使用了驼峰命名")
        
        assert len(violations) == 0, "以下路径使用了驼峰命名:\n" + "\n".join(violations)


# **Feature: api-optimization, 辅助测试: URL结构完整性**
class TestUrlStructureIntegrity:
    """
    辅助测试: 验证URL结构的完整性和正确性。
    """
    
    def test_all_urls_resolvable(self):
        """所有URL应可正确解析。"""
        api_urls = get_api_endpoint_urls()
        
        # 验证至少有端点注册
        assert len(api_urls) > 0, "没有找到任何API端点"
        
        # 验证每个端点都有名称
        unnamed = [url for url in api_urls if url[1] is None]
        assert len(unnamed) == 0, f"以下端点缺少名称: {unnamed}"
    
    def test_expected_endpoints_exist(self):
        """验证预期的关键端点都已注册。"""
        api_urls = get_api_endpoint_urls()
        patterns = [url[0] for url in api_urls]
        
        # 关键端点列表
        expected_endpoints = [
            # 岗位管理
            'api/positions/',
            'api/positions/ai/generate/',
            # 简历库
            'api/library/',
            'api/library/batch-delete/',
            'api/library/check-hash/',
            # 简历筛选
            'api/screening/',
            'api/screening/tasks/',
            'api/screening/groups/',
            'api/screening/data/',
            # 视频分析
            'api/videos/',
            'api/videos/upload/',
            # 最终推荐
            # api/recommend/analysis/<uuid:resume_id>/ 是动态路径
            # 面试辅助
            'api/interviews/sessions/',
        ]
        
        for expected in expected_endpoints:
            assert expected in patterns, f"缺少预期端点: {expected}"
