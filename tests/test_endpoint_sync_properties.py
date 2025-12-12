"""
前后端端点同步属性测试。

Property 12: 前后端端点同步
验证后端 Django URL 配置与前端 TypeScript 端点常量保持一致。

Validates: Requirements 8.1
"""
import re
import pytest
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


# 项目路径
BACKEND_ROOT = Path(__file__).parent.parent
FRONTEND_ROOT = BACKEND_ROOT.parent / "HRM2-Vue-Frontend_new"


@dataclass
class EndpointInfo:
    """端点信息"""
    path: str
    name: str = ""
    module: str = ""
    
    def normalized_path(self) -> str:
        """规范化路径，将参数占位符统一为 {param} 格式"""
        # Django: <uuid:xxx> -> {param}
        path = re.sub(r'<uuid:\w+>', '{param}', self.path)
        # Django: <int:xxx> -> {param}
        path = re.sub(r'<int:\w+>', '{param}', path)
        # Django: <str:xxx> -> {param}
        path = re.sub(r'<str:\w+>', '{param}', path)
        # 前端: ${xxx} -> {param}
        path = re.sub(r'\$\{\w+\}', '{param}', path)
        return path


def parse_backend_urls() -> Dict[str, List[EndpointInfo]]:
    """解析后端 Django URL 配置"""
    endpoints: Dict[str, List[EndpointInfo]] = {}
    
    url_modules = {
        'positions': BACKEND_ROOT / 'apps' / 'position_settings' / 'urls.py',
        'library': BACKEND_ROOT / 'apps' / 'resume_library' / 'urls.py',
        'screening': BACKEND_ROOT / 'apps' / 'resume_screening' / 'urls.py',
        'videos': BACKEND_ROOT / 'apps' / 'video_analysis' / 'urls.py',
        'recommend': BACKEND_ROOT / 'apps' / 'final_recommend' / 'urls.py',
        'interviews': BACKEND_ROOT / 'apps' / 'interview_assist' / 'urls.py',
    }
    
    for module_name, url_file in url_modules.items():
        if not url_file.exists():
            continue
            
        content = url_file.read_text(encoding='utf-8')
        endpoints[module_name] = []
        
        path_pattern = r"path\(['\"]([^'\"]*)['\"].*?name=['\"]([^'\"]+)['\"]"
        
        for match in re.finditer(path_pattern, content, re.DOTALL):
            path_str = match.group(1)
            name = match.group(2)
            
            full_path = f"/api/{module_name}/{path_str}"
            full_path = re.sub(r'//+', '/', full_path)
            
            endpoints[module_name].append(EndpointInfo(
                path=full_path,
                name=name,
                module=module_name
            ))
    
    return endpoints


def _get_module_from_path(path: str) -> str:
    """根据路径推断模块名"""
    path_module_mapping = {
        '/positions/': 'positions',
        '/library/': 'library',
        '/screening/': 'screening',
        '/videos/': 'videos',
        '/recommend/': 'recommend',
        '/interviews/': 'interviews',
    }
    for prefix, module in path_module_mapping.items():
        if path.startswith(prefix):
            return module
    return ""


def parse_frontend_endpoints() -> Dict[str, List[EndpointInfo]]:
    """解析前端 TypeScript 端点常量"""
    endpoints: Dict[str, List[EndpointInfo]] = {}
    
    endpoint_file = FRONTEND_ROOT / 'src' / 'api' / 'endpoints.ts'
    if not endpoint_file.exists():
        return endpoints
    
    content = endpoint_file.read_text(encoding='utf-8')
    
    # 初始化所有模块
    for module in ['positions', 'library', 'screening', 'videos', 'recommend', 'interviews']:
        endpoints[module] = []
    
    # 规范化内容
    normalized = re.sub(r'\s+', ' ', content)
    
    # 匹配简单端点
    simple_pattern = r"(\w+):\s*['\"](/[^'\"]+)['\"]"
    for match in re.finditer(simple_pattern, normalized):
        name = match.group(1)
        path = match.group(2)
        module = _get_module_from_path(path)
        if module:
            endpoints[module].append(EndpointInfo(
                path=f"/api{path}",
                name=name,
                module=module
            ))
    
    # 匹配函数端点
    func_pattern = r"(\w+):\s*\([^)]*\)\s*=>\s*`(/[^`]+)`"
    for match in re.finditer(func_pattern, normalized):
        name = match.group(1)
        path = match.group(2)
        module = _get_module_from_path(path)
        if module:
            endpoints[module].append(EndpointInfo(
                path=f"/api{path}",
                name=name,
                module=module
            ))
    
    return endpoints


@pytest.fixture(scope="module")
def backend_endpoints():
    """后端端点 fixture"""
    return parse_backend_urls()


@pytest.fixture(scope="module")
def frontend_endpoints():
    """前端端点 fixture"""
    return parse_frontend_endpoints()


# **Feature: api-optimization, Property 12: 前后端端点同步**
class TestEndpointSync:
    """
    Property 12: 前后端端点同步
    
    验证后端 Django URL 配置与前端 TypeScript 端点常量保持一致。
    
    Validates: Requirements 8.1
    """
    
    def test_frontend_endpoints_file_exists(self):
        """前端端点常量文件应存在"""
        endpoint_file = FRONTEND_ROOT / 'src' / 'api' / 'endpoints.ts'
        assert endpoint_file.exists(), f"前端端点文件不存在: {endpoint_file}"
    
    def test_all_modules_have_backend_urls(self, backend_endpoints):
        """所有模块应有后端 URL 配置"""
        expected_modules = {'positions', 'library', 'screening', 'videos', 'recommend', 'interviews'}
        actual_modules = set(backend_endpoints.keys())
        missing = expected_modules - actual_modules
        assert not missing, f"缺少后端模块: {missing}"
    
    def test_all_modules_have_frontend_endpoints(self, frontend_endpoints):
        """所有模块应有前端端点定义"""
        expected_modules = {'positions', 'library', 'screening', 'videos', 'recommend', 'interviews'}
        actual_modules = {m for m, eps in frontend_endpoints.items() if eps}
        missing = expected_modules - actual_modules
        assert not missing, f"缺少前端模块端点: {missing}"
    
    def test_backend_endpoint_count_matches_frontend(self, backend_endpoints, frontend_endpoints):
        """后端端点数量应与前端端点数量一致"""
        backend_count = sum(len(eps) for eps in backend_endpoints.values())
        frontend_count = sum(len(eps) for eps in frontend_endpoints.values())
        assert backend_count == frontend_count, \
            f"端点数量不匹配: 后端={backend_count}, 前端={frontend_count}"
    
    def test_positions_module_sync(self, backend_endpoints, frontend_endpoints):
        """岗位管理模块端点应同步"""
        self._check_module_sync('positions', backend_endpoints, frontend_endpoints)
    
    def test_library_module_sync(self, backend_endpoints, frontend_endpoints):
        """简历库模块端点应同步"""
        self._check_module_sync('library', backend_endpoints, frontend_endpoints)
    
    def test_screening_module_sync(self, backend_endpoints, frontend_endpoints):
        """简历筛选模块端点应同步"""
        self._check_module_sync('screening', backend_endpoints, frontend_endpoints)
    
    def test_videos_module_sync(self, backend_endpoints, frontend_endpoints):
        """视频分析模块端点应同步"""
        self._check_module_sync('videos', backend_endpoints, frontend_endpoints)
    
    def test_recommend_module_sync(self, backend_endpoints, frontend_endpoints):
        """最终推荐模块端点应同步"""
        self._check_module_sync('recommend', backend_endpoints, frontend_endpoints)
    
    def test_interviews_module_sync(self, backend_endpoints, frontend_endpoints):
        """面试辅助模块端点应同步"""
        self._check_module_sync('interviews', backend_endpoints, frontend_endpoints)
    
    def test_no_backend_only_endpoints(self, backend_endpoints, frontend_endpoints):
        """不应有仅后端存在的端点"""
        backend_only = []
        for module in backend_endpoints:
            backend_paths = {ep.normalized_path() for ep in backend_endpoints.get(module, [])}
            frontend_paths = {ep.normalized_path() for ep in frontend_endpoints.get(module, [])}
            for ep in backend_endpoints.get(module, []):
                if ep.normalized_path() not in frontend_paths:
                    backend_only.append(f"[{module}] {ep.path}")
        
        assert not backend_only, \
            f"发现仅后端存在的端点:\n" + "\n".join(backend_only)
    
    def test_no_frontend_only_endpoints(self, backend_endpoints, frontend_endpoints):
        """不应有仅前端存在的端点"""
        frontend_only = []
        for module in frontend_endpoints:
            backend_paths = {ep.normalized_path() for ep in backend_endpoints.get(module, [])}
            frontend_paths = {ep.normalized_path() for ep in frontend_endpoints.get(module, [])}
            for ep in frontend_endpoints.get(module, []):
                if ep.normalized_path() not in backend_paths:
                    frontend_only.append(f"[{module}] {ep.path}")
        
        assert not frontend_only, \
            f"发现仅前端存在的端点:\n" + "\n".join(frontend_only)
    
    def _check_module_sync(
        self, 
        module: str, 
        backend_endpoints: Dict[str, List[EndpointInfo]], 
        frontend_endpoints: Dict[str, List[EndpointInfo]]
    ):
        """检查单个模块的端点同步状态"""
        backend_eps = backend_endpoints.get(module, [])
        frontend_eps = frontend_endpoints.get(module, [])
        
        backend_paths = {ep.normalized_path() for ep in backend_eps}
        frontend_paths = {ep.normalized_path() for ep in frontend_eps}
        
        # 检查后端特有
        backend_only = backend_paths - frontend_paths
        assert not backend_only, \
            f"{module}模块: 后端存在但前端缺少的端点: {backend_only}"
        
        # 检查前端特有
        frontend_only = frontend_paths - backend_paths
        assert not frontend_only, \
            f"{module}模块: 前端存在但后端缺少的端点: {frontend_only}"


class TestEndpointNamingConsistency:
    """
    端点命名一致性测试
    
    验证前后端端点命名规范。
    """
    
    def test_backend_paths_use_kebab_case(self, backend_endpoints):
        """后端路径应使用 kebab-case 命名"""
        invalid_paths = []
        for module, endpoints in backend_endpoints.items():
            for ep in endpoints:
                # 提取路径中的非参数部分
                path_parts = ep.path.split('/')
                for part in path_parts:
                    if part and not part.startswith('<') and not part.startswith('{'):
                        # 检查是否使用了下划线（应该用连字符）
                        if '_' in part:
                            invalid_paths.append(f"[{module}] {ep.path} (contains underscore in: {part})")
        
        assert not invalid_paths, \
            f"后端路径应使用kebab-case:\n" + "\n".join(invalid_paths)
    
    def test_frontend_constants_use_screaming_snake_case(self, frontend_endpoints):
        """前端端点常量应使用 SCREAMING_SNAKE_CASE 命名"""
        invalid_names = []
        for module, endpoints in frontend_endpoints.items():
            for ep in endpoints:
                # 检查是否全大写+下划线
                if not re.match(r'^[A-Z][A-Z0-9_]*$', ep.name):
                    invalid_names.append(f"[{module}] {ep.name}")
        
        assert not invalid_names, \
            f"前端常量应使用SCREAMING_SNAKE_CASE:\n" + "\n".join(invalid_names)
    
    def test_all_backend_endpoints_have_names(self, backend_endpoints):
        """所有后端端点应有名称"""
        unnamed = []
        for module, endpoints in backend_endpoints.items():
            for ep in endpoints:
                if not ep.name:
                    unnamed.append(f"[{module}] {ep.path}")
        
        assert not unnamed, f"发现未命名的后端端点:\n" + "\n".join(unnamed)


class TestEndpointStructure:
    """
    端点结构测试
    
    验证端点定义的结构完整性。
    """
    
    def test_all_modules_in_main_urls(self):
        """所有模块应在主 URL 配置中注册"""
        main_urls = BACKEND_ROOT / 'config' / 'urls.py'
        content = main_urls.read_text(encoding='utf-8')
        
        expected_includes = [
            "include('apps.position_settings.urls')",
            "include('apps.resume_library.urls')",
            "include('apps.resume_screening.urls')",
            "include('apps.video_analysis.urls')",
            "include('apps.final_recommend.urls')",
            "include('apps.interview_assist.urls')",
        ]
        
        for include in expected_includes:
            assert include in content, f"主URL配置中缺少: {include}"
    
    def test_api_prefix_in_main_urls(self):
        """主 URL 配置应使用 /api/ 前缀"""
        main_urls = BACKEND_ROOT / 'config' / 'urls.py'
        content = main_urls.read_text(encoding='utf-8')
        
        # 检查所有业务模块路由都使用 api/ 前缀
        module_patterns = [
            r"path\(['\"]api/positions/",
            r"path\(['\"]api/library/",
            r"path\(['\"]api/screening/",
            r"path\(['\"]api/videos/",
            r"path\(['\"]api/recommend/",
            r"path\(['\"]api/interviews/",
        ]
        
        for pattern in module_patterns:
            assert re.search(pattern, content), f"URL配置缺少正确的api前缀: {pattern}"
    
    def test_frontend_endpoints_base_path(self, frontend_endpoints):
        """前端端点应使用正确的基础路径"""
        for module, endpoints in frontend_endpoints.items():
            for ep in endpoints:
                assert ep.path.startswith('/api/'), \
                    f"前端端点应以/api/开头: {ep.path}"
