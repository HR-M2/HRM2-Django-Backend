"""
API文档生成脚本 - 基于 drf-spectacular OpenAPI Schema

运行方式: python Docs/生成API文档.py
输出: API参考文档.md

使用 drf-spectacular 生成 OpenAPI 3.0 规范，然后转换为易读的 Markdown 文档。
包含请求参数、响应格式等详细信息。
"""
import os
import sys
import json
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


# ========== 配置区域 ==========
# 模块中文名称映射（与 SPECTACULAR_SETTINGS['TAGS'] 对应）
TAG_TITLES = {
    'positions': '岗位设置',
    'library': '简历库',
    'screening': '简历筛选',
    'videos': '视频分析',
    'interviews': '面试辅助',
    'recommend': '最终推荐',
}

# HTTP方法顺序和样式
METHOD_ORDER = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
METHOD_BADGES = {
    'GET': '🟢 GET',
    'POST': '🟡 POST',
    'PUT': '🟠 PUT',
    'PATCH': '🟠 PATCH',
    'DELETE': '🔴 DELETE',
}
# ==============================


def get_openapi_schema():
    """使用 drf-spectacular 生成 OpenAPI Schema"""
    from drf_spectacular.generators import SchemaGenerator
    
    generator = SchemaGenerator()
    schema = generator.get_schema(request=None, public=True)
    return schema


def extract_tag_from_path(path):
    """从路径提取标签"""
    # 新的 /api/ 前缀路径映射
    tag_mapping = {
        '/api/positions/': 'positions',
        '/api/library/': 'library',
        '/api/screening/': 'screening',
        '/api/videos/': 'videos',
        '/api/interviews/': 'interviews',
        '/api/recommend/': 'recommend',
    }
    for prefix, tag in tag_mapping.items():
        if path.startswith(prefix):
            return tag
    return 'other'


def format_schema_type(schema):
    """格式化 Schema 类型为可读字符串"""
    if not schema:
        return 'any'
    
    schema_type = schema.get('type', '')
    
    if '$ref' in schema:
        # 引用类型，提取名称
        ref = schema['$ref']
        return ref.split('/')[-1]
    
    if schema_type == 'array':
        items = schema.get('items', {})
        item_type = format_schema_type(items)
        return f'{item_type}[]'
    
    if schema_type == 'object':
        return 'object'
    
    if 'anyOf' in schema:
        types = [format_schema_type(s) for s in schema['anyOf']]
        return ' | '.join(types)
    
    return schema_type or 'any'


def format_parameters(parameters):
    """格式化请求参数"""
    if not parameters:
        return None
    
    lines = []
    for param in parameters:
        name = param.get('name', '')
        location = param.get('in', '')  # path, query, header
        required = '必填' if param.get('required') else '可选'
        schema = param.get('schema', {})
        param_type = format_schema_type(schema)
        description = param.get('description', '')
        
        lines.append(f"  - `{name}` ({param_type}, {location}, {required}): {description}")
    
    return '\n'.join(lines) if lines else None


def format_request_body(request_body):
    """格式化请求体"""
    if not request_body:
        return None
    
    content = request_body.get('content', {})
    json_content = content.get('application/json', {})
    schema = json_content.get('schema', {})
    
    if not schema:
        return None
    
    return format_schema_type(schema)


def format_responses(responses):
    """格式化响应"""
    if not responses:
        return None
    
    lines = []
    for status_code, response in responses.items():
        description = response.get('description', '')
        content = response.get('content', {})
        
        if content:
            json_content = content.get('application/json', {})
            schema = json_content.get('schema', {})
            schema_type = format_schema_type(schema)
            lines.append(f"  - `{status_code}`: {description} → `{schema_type}`")
        else:
            lines.append(f"  - `{status_code}`: {description}")
    
    return '\n'.join(lines) if lines else None


def generate_markdown(schema):
    """从 OpenAPI Schema 生成 Markdown 文档"""
    lines = []
    
    # 基本信息
    info = schema.get('info', {})
    title = info.get('title', 'API文档')
    version = info.get('version', '1.0.0')
    description = info.get('description', '')
    
    lines.append(f"# {title}\n")
    lines.append(f"> **版本**: {version}")
    lines.append(f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if description:
        lines.append(description.strip())
        lines.append("")
    
    lines.append("---\n")
    
    # 按标签分组
    paths = schema.get('paths', {})
    tags_data = {}  # tag -> [(path, method, operation), ...]
    
    for path, methods in paths.items():
        tag = extract_tag_from_path(path)
        
        for method, operation in methods.items():
            if method.upper() not in METHOD_ORDER:
                continue
            
            if tag not in tags_data:
                tags_data[tag] = []
            tags_data[tag].append((path, method.upper(), operation))
    
    # 统计
    total_endpoints = sum(len(ops) for ops in tags_data.values())
    lines.append(f"## 概览\n")
    lines.append(f"共 **{total_endpoints}** 个API端点，分布在 **{len(tags_data)}** 个模块中。\n")
    
    # 目录
    lines.append("## 目录\n")
    for tag in tags_data.keys():
        title = TAG_TITLES.get(tag, tag)
        count = len(tags_data[tag])
        anchor = tag.replace('-', '-')
        lines.append(f"- [{title}](#{anchor}) ({count}个接口)")
    lines.append("\n---\n")
    
    # 快速参考表（每个模块）
    lines.append("## 快速参考\n")
    
    for tag, operations in tags_data.items():
        title = TAG_TITLES.get(tag, tag)
        lines.append(f"### {title}\n")
        lines.append("| 方法 | 路径 | 说明 |")
        lines.append("|:-----|:-----|:-----|")
        
        # 按方法排序
        operations.sort(key=lambda x: (x[0], METHOD_ORDER.index(x[1]) if x[1] in METHOD_ORDER else 99))
        
        for path, method, operation in operations:
            summary = operation.get('summary', '') or operation.get('operationId', '')
            badge = METHOD_BADGES.get(method, method)
            # 格式化路径参数
            formatted_path = path.replace('{', '`{').replace('}', '}`')
            lines.append(f"| {badge} | {formatted_path} | {summary} |")
        
        lines.append("")
    
    lines.append("---\n")
    
    # 详细说明
    lines.append("## 接口详情\n")
    
    for tag, operations in tags_data.items():
        title = TAG_TITLES.get(tag, tag)
        lines.append(f"### {title}\n")
        
        operations.sort(key=lambda x: (x[0], METHOD_ORDER.index(x[1]) if x[1] in METHOD_ORDER else 99))
        
        for path, method, operation in operations:
            summary = operation.get('summary', '')
            description = operation.get('description', '')
            operation_id = operation.get('operationId', '')
            
            badge = METHOD_BADGES.get(method, method)
            lines.append(f"#### {badge} `{path}`\n")
            
            if summary:
                lines.append(f"**{summary}**\n")
            
            if description and description != summary:
                lines.append(f"{description}\n")
            
            # 路径/查询参数
            parameters = operation.get('parameters', [])
            params_str = format_parameters(parameters)
            if params_str:
                lines.append("**参数**:\n")
                lines.append(params_str)
                lines.append("")
            
            # 请求体
            request_body = operation.get('requestBody', {})
            body_type = format_request_body(request_body)
            if body_type:
                lines.append(f"**请求体**: `{body_type}`\n")
            
            # 响应
            responses = operation.get('responses', {})
            responses_str = format_responses(responses)
            if responses_str:
                lines.append("**响应**:\n")
                lines.append(responses_str)
                lines.append("")
            
            lines.append("---\n")
    
    # 数据模型（如果有的话）
    components = schema.get('components', {})
    schemas = components.get('schemas', {})
    
    if schemas:
        lines.append("## 数据模型\n")
        lines.append("以下是API中使用的主要数据结构：\n")
        
        for name, schema_def in schemas.items():
            # 跳过内部类型
            if name.startswith('Patched') or name.startswith('Paginated'):
                continue
            
            lines.append(f"### {name}\n")
            
            description = schema_def.get('description', '')
            if description:
                lines.append(f"{description}\n")
            
            properties = schema_def.get('properties', {})
            required = schema_def.get('required', [])
            
            if properties:
                lines.append("| 字段 | 类型 | 必填 | 说明 |")
                lines.append("|:-----|:-----|:-----|:-----|")
                
                for prop_name, prop_schema in properties.items():
                    prop_type = format_schema_type(prop_schema)
                    is_required = '是' if prop_name in required else '否'
                    prop_desc = prop_schema.get('description', '-')
                    lines.append(f"| `{prop_name}` | {prop_type} | {is_required} | {prop_desc} |")
                
                lines.append("")
    
    return '\n'.join(lines)


def main():
    print("正在生成 OpenAPI Schema...")
    
    try:
        schema = get_openapi_schema()
    except Exception as e:
        print(f"错误: 无法生成 OpenAPI Schema - {e}")
        print("请确保已安装 drf-spectacular 并正确配置")
        return 1
    
    paths = schema.get('paths', {})
    endpoint_count = sum(len([m for m in methods.keys() if m.upper() in METHOD_ORDER]) 
                         for methods in paths.values())
    
    print(f"✅ 找到 {endpoint_count} 个API端点")
    
    # 生成Markdown
    print("正在生成 Markdown 文档...")
    markdown = generate_markdown(schema)
    
    # 保存文档
    output_path = Path(__file__).parent / 'API参考文档.md'
    output_path.write_text(markdown, encoding='utf-8')
    print(f"✅ 文档已生成: {output_path}")
    
    # 同时保存 OpenAPI JSON（可选，用于其他工具）
    json_path = Path(__file__).parent / 'openapi.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
    print(f"✅ OpenAPI Schema 已保存: {json_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
