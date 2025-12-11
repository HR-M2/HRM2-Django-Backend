"""
API文档生成脚本 - 使用Django官方API提取所有路由

运行方式: 在Docs目录下执行 python 生成API文档.py
输出: API参考文档.md
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# 设置Django环境
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# 加载 .env 文件
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

# 设置 Django settings（默认开发环境）
env = os.getenv('DJANGO_ENV', 'development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{env}')

import django
django.setup()

from django.urls import get_resolver, URLPattern, URLResolver


# ========== 配置区域 ==========
# 添加新模块时，在此处添加中文名称映射
APP_TITLES = {
    'position_settings': '岗位设置',
    'resume_screening': '简历筛选',
    'video_analysis': '视频分析',
    'final_recommend': '最终推荐',
    'interview_assist': '面试辅助',
    'other': '其他',
    # 新增模块示例: 'new_module': '新模块',
}
# ==============================


def is_method_overridden(cls, method_name):
    """检查方法是否在当前类中重写（非继承自基类）"""
    if not hasattr(cls, method_name):
        return False
    
    method = getattr(cls, method_name)
    if not callable(method):
        return False
    
    # 检查方法是否定义在当前类中（而非基类）
    for base in cls.__mro__[1:]:  # 跳过当前类本身
        if hasattr(base, method_name):
            base_method = getattr(base, method_name)
            # 如果当前方法与基类方法相同，说明是继承的
            if method == base_method:
                return False
            # 如果不同，说明被重写了
            return True
    
    # 没有基类有此方法，说明是新定义的
    return True


def get_view_info(callback):
    """从视图回调中提取信息"""
    view_class = getattr(callback, 'view_class', None) or getattr(callback, 'cls', None)
    
    if view_class:
        # 类视图
        class_name = view_class.__name__
        docstring = (view_class.__doc__ or '').strip().split('\n')[0]  # 取第一行
        
        # 获取支持的HTTP方法（只检查真正实现的）
        methods = []
        for method in ['get', 'post', 'put', 'patch', 'delete']:
            handler_name = f'handle_{method}'
            standard_name = method
            
            # 优先检查 handle_xxx (SafeAPIView 风格)
            if is_method_overridden(view_class, handler_name):
                handler = getattr(view_class, handler_name)
                method_doc = (handler.__doc__ or '').strip().split('\n')[0]
                methods.append({
                    'method': method.upper(),
                    'description': method_doc or docstring
                })
            # 再检查标准 DRF 风格 (get, post, etc.)
            elif is_method_overridden(view_class, standard_name):
                handler = getattr(view_class, standard_name)
                method_doc = (handler.__doc__ or '').strip().split('\n')[0]
                methods.append({
                    'method': method.upper(),
                    'description': method_doc or docstring
                })
        
        return {
            'class_name': class_name,
            'docstring': docstring,
            'methods': methods
        }
    else:
        # 函数视图
        func_name = getattr(callback, '__name__', str(callback))
        docstring = (getattr(callback, '__doc__', '') or '').strip().split('\n')[0]
        return {
            'class_name': func_name,
            'docstring': docstring,
            'methods': [{'method': 'ALL', 'description': docstring}]
        }


def extract_urls(urlpatterns, prefix='', app_name=None):
    """递归提取所有URL"""
    urls = []
    
    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            # 递归处理嵌套路由
            nested_prefix = prefix + str(pattern.pattern)
            nested_app = pattern.namespace or app_name
            urls.extend(extract_urls(pattern.url_patterns, nested_prefix, nested_app))
        elif isinstance(pattern, URLPattern):
            # 提取路由信息
            path = prefix + str(pattern.pattern)
            name = pattern.name or ''
            
            # 获取视图信息
            view_info = get_view_info(pattern.callback)
            
            urls.append({
                'path': '/' + path.rstrip('/') + '/' if path else '/',
                'name': name,
                'app': app_name or '',
                **view_info
            })
    
    return urls


def generate_markdown(urls):
    """生成Markdown文档"""
    lines = []
    
    # 标题
    lines.append("# HRM2 后端 API 参考文档\n")
    lines.append(f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"> 共 {len(urls)} 个API端点\n")
    lines.append("---\n")
    
    # 目录
    lines.append("## 目录\n")
    apps = {}
    for url in urls:
        app = url['app'] or 'other'
        if app not in apps:
            apps[app] = []
        apps[app].append(url)
    
    for app in apps.keys():
        title = APP_TITLES.get(app, app)
        lines.append(f"- [{title}](#{app})")
    lines.append("\n---\n")
    
    # 按模块输出
    for app, app_urls in apps.items():
        title = APP_TITLES.get(app, app)
        lines.append(f"## {title} {{{app}}}\n")
        
        # 表格头
        lines.append("| 方法 | 路径 | 说明 |")
        lines.append("|------|------|------|")
        
        for url in app_urls:
            path = url['path']
            # 将UUID参数格式化
            path = path.replace('<uuid:', '{').replace('>', '}')
            path = path.replace('<int:', '{').replace('<str:', '{').replace('<path:', '{')
            
            if url['methods']:
                for m in url['methods']:
                    method = m['method']
                    desc = m['description'] or url['docstring'] or url['class_name']
                    # 截断过长描述
                    if len(desc) > 50:
                        desc = desc[:47] + '...'
                    lines.append(f"| `{method}` | `{path}` | {desc} |")
            else:
                desc = url['docstring'] or url['class_name']
                if len(desc) > 50:
                    desc = desc[:47] + '...'
                lines.append(f"| - | `{path}` | {desc} |")
        
        lines.append("\n")
    
    # 详细说明
    lines.append("---\n")
    lines.append("## API 详细说明\n")
    
    for app, app_urls in apps.items():
        title = APP_TITLES.get(app, app)
        lines.append(f"### {title}\n")
        
        for url in app_urls:
            path = url['path'].replace('<uuid:', '{').replace('>', '}')
            path = path.replace('<int:', '{').replace('<str:', '{').replace('<path:', '{')
            
            lines.append(f"#### `{path}`\n")
            lines.append(f"- **视图**: `{url['class_name']}`")
            if url['docstring']:
                lines.append(f"- **描述**: {url['docstring']}")
            if url['name']:
                lines.append(f"- **路由名**: `{url['name']}`")
            
            if url['methods']:
                lines.append("- **方法**:")
                for m in url['methods']:
                    desc = m['description'] or '无描述'
                    lines.append(f"  - `{m['method']}`: {desc}")
            
            lines.append("\n")
    
    return '\n'.join(lines)


def main():
    print("正在提取API路由...")
    
    # 获取Django根URL配置
    resolver = get_resolver()
    urls = extract_urls(resolver.url_patterns)
    
    # 过滤掉admin和静态文件路由
    urls = [u for u in urls if not u['path'].startswith('/admin') 
            and not u['path'].startswith('/static')
            and not u['path'].startswith('/__debug__')]
    
    print(f"找到 {len(urls)} 个API端点")
    
    # 生成Markdown
    markdown = generate_markdown(urls)
    
    # 保存到Docs目录
    output_path = Path(__file__).parent / 'API参考文档.md'
    output_path.write_text(markdown, encoding='utf-8')
    
    print(f"文档已生成: {output_path}")


if __name__ == '__main__':
    main()
