"""
API分析脚本 - 分析HRM2-Django-Backend中所有API的请求和响应结构
生成Markdown文档保存到Docs文件夹

运行方式: python Docs/分析API.py
"""
import os
import re
import ast
from pathlib import Path
from datetime import datetime


class APIAnalyzer:
    """API分析器类"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.apps_path = self.base_path / 'apps'
        self.docs_path = self.base_path / 'Docs'
        self.apis = []
        
    def analyze(self):
        """执行分析"""
        print("开始分析API...")
        
        # 确保Docs目录存在
        self.docs_path.mkdir(exist_ok=True)
        
        # 分析各个模块
        modules = [
            'position_settings',
            'resume_screening',
            'video_analysis',
            'final_recommend',
            'interview_assist'
        ]
        
        for module in modules:
            self._analyze_module(module)
        
        # 生成报告
        self._generate_report()
        
        print(f"分析完成！报告已保存到 {self.docs_path / 'API分析报告.md'}")
    
    def _analyze_module(self, module_name: str):
        """分析单个模块"""
        module_path = self.apps_path / module_name
        
        # 读取urls.py获取路由信息
        urls_file = module_path / 'urls.py'
        routes = self._parse_urls(urls_file) if urls_file.exists() else []
        
        # 读取views文件
        views_path = module_path / 'views.py'
        if views_path.exists():
            self._analyze_views_file(views_path, module_name, routes)
        
        # 检查views目录
        views_dir = module_path / 'views'
        if views_dir.exists() and views_dir.is_dir():
            for view_file in views_dir.glob('*.py'):
                if view_file.name != '__init__.py':
                    self._analyze_views_file(view_file, module_name, routes)
    
    def _parse_urls(self, urls_file: Path) -> list:
        """解析urls.py获取路由信息"""
        routes = []
        content = urls_file.read_text(encoding='utf-8')
        
        # 使用正则表达式匹配path定义
        pattern = r"path\(['\"]([^'\"]*)['\"],\s*(\w+)(?:\.as_view\(\))?,\s*name=['\"]([^'\"]*)['\"]"
        matches = re.findall(pattern, content)
        
        for match in matches:
            routes.append({
                'path': match[0],
                'view': match[1],
                'name': match[2]
            })
        
        return routes
    
    def _analyze_views_file(self, views_file: Path, module_name: str, routes: list):
        """分析views文件"""
        content = views_file.read_text(encoding='utf-8')
        
        # 分析响应类型使用情况
        response_types = self._analyze_response_types(content)
        
        # 提取视图类和方法
        views = self._extract_views(content, views_file.name)
        
        for view in views:
            view['module'] = module_name
            view['file'] = views_file.name
            view['response_types'] = response_types
            
            # 匹配路由
            for route in routes:
                if route['view'] == view['class_name'] or route['view'] in view['class_name']:
                    view['route'] = route
                    break
            
            self.apis.append(view)
    
    def _analyze_response_types(self, content: str) -> dict:
        """分析响应类型使用情况"""
        types = {
            'JsonResponse': {
                'imported': 'JsonResponse' in content,
                'used': bool(re.search(r'return\s+JsonResponse', content)),
                'count': len(re.findall(r'return\s+JsonResponse', content))
            },
            'Response': {
                'imported': 'from rest_framework.response import Response' in content or 'from rest_framework import' in content,
                'used': bool(re.search(r'return\s+Response\(', content)),
                'count': len(re.findall(r'return\s+Response\(', content))
            },
            'APIResponse': {
                'imported': 'from apps.common.response import APIResponse' in content,
                'used': bool(re.search(r'return\s+APIResponse', content)),
                'count': len(re.findall(r'return\s+APIResponse', content))
            },
            'FileResponse': {
                'imported': 'FileResponse' in content,
                'used': bool(re.search(r'return\s+FileResponse', content)),
                'count': len(re.findall(r'return\s+FileResponse', content))
            }
        }
        return types
    
    def _extract_views(self, content: str, filename: str) -> list:
        """提取视图类和方法信息"""
        views = []
        
        # 匹配类定义
        class_pattern = r'class\s+(\w+)\s*\(.*?SafeAPIView.*?\):\s*(?:"""([^"]*?)""")?\s*((?:.*?(?=class\s+\w+|$)))'
        class_matches = re.findall(class_pattern, content, re.DOTALL)
        
        for match in class_matches:
            class_name = match[0]
            docstring = match[1].strip() if match[1] else ''
            class_body = match[2]
            
            methods = self._extract_methods(class_body)
            responses = self._extract_responses(class_body)
            request_params = self._extract_request_params(class_body)
            
            views.append({
                'class_name': class_name,
                'docstring': docstring,
                'methods': methods,
                'responses': responses,
                'request_params': request_params
            })
        
        return views
    
    def _extract_methods(self, class_body: str) -> list:
        """提取视图方法"""
        methods = []
        method_pattern = r'def\s+(handle_(?:get|post|put|delete|patch))\s*\(self,\s*request(?:,\s*([^)]*))?\):\s*(?:"""([^"]*?)""")?'
        matches = re.findall(method_pattern, class_body)
        
        for match in matches:
            method_name = match[0]
            params = match[1].strip() if match[1] else ''
            docstring = match[2].strip() if match[2] else ''
            
            http_method = method_name.replace('handle_', '').upper()
            
            methods.append({
                'name': method_name,
                'http_method': http_method,
                'url_params': params,
                'docstring': docstring
            })
        
        return methods
    
    def _extract_responses(self, class_body: str) -> list:
        """提取响应结构"""
        responses = []
        
        # 匹配JsonResponse返回
        json_pattern = r'return\s+JsonResponse\(\s*(\{[^}]+(?:\{[^}]*\}[^}]*)*\})'
        json_matches = re.findall(json_pattern, class_body, re.DOTALL)
        for match in json_matches:
            responses.append({
                'type': 'JsonResponse',
                'structure': self._clean_response_structure(match)
            })
        
        # 匹配Response返回
        response_pattern = r'return\s+Response\(\s*(\{[^}]+(?:\{[^}]*\}[^}]*)*\})'
        response_matches = re.findall(response_pattern, class_body, re.DOTALL)
        for match in response_matches:
            responses.append({
                'type': 'Response',
                'structure': self._clean_response_structure(match)
            })
        
        # 匹配APIResponse返回
        api_pattern = r'return\s+APIResponse\.(\w+)\('
        api_matches = re.findall(api_pattern, class_body)
        for match in api_matches:
            responses.append({
                'type': 'APIResponse',
                'method': match
            })
        
        return responses
    
    def _extract_request_params(self, class_body: str) -> list:
        """提取请求参数"""
        params = []
        
        # 匹配get_param调用
        param_pattern = r"self\.get_param\s*\(\s*request\s*,\s*['\"](\w+)['\"](?:\s*,\s*(?:required\s*=\s*(\w+)|default\s*=\s*([^)]+)))?\)"
        matches = re.findall(param_pattern, class_body)
        
        for match in matches:
            param_name = match[0]
            required = match[1].lower() == 'true' if match[1] else False
            default = match[2].strip() if match[2] else None
            
            params.append({
                'name': param_name,
                'required': required,
                'default': default
            })
        
        # 匹配get_int_param调用
        int_param_pattern = r"self\.get_int_param\s*\(\s*request\s*,\s*['\"](\w+)['\"]"
        int_matches = re.findall(int_param_pattern, class_body)
        for match in int_matches:
            params.append({
                'name': match,
                'type': 'int',
                'required': False
            })
        
        # 匹配request.data.get调用
        data_pattern = r"request\.data\.get\s*\(\s*['\"](\w+)['\"]"
        data_matches = re.findall(data_pattern, class_body)
        for match in data_matches:
            if not any(p['name'] == match for p in params):
                params.append({
                    'name': match,
                    'source': 'request.data'
                })
        
        # 匹配request.GET.get调用
        get_pattern = r"request\.GET\.get\s*\(\s*['\"](\w+)['\"]"
        get_matches = re.findall(get_pattern, class_body)
        for match in get_matches:
            if not any(p['name'] == match for p in params):
                params.append({
                    'name': match,
                    'source': 'request.GET'
                })
        
        # 匹配request.FILES.get调用
        files_pattern = r"request\.FILES\.get\s*\(\s*['\"](\w+)['\"]"
        files_matches = re.findall(files_pattern, class_body)
        for match in files_matches:
            params.append({
                'name': match,
                'source': 'request.FILES',
                'type': 'file'
            })
        
        return params
    
    def _clean_response_structure(self, structure: str) -> str:
        """清理响应结构字符串"""
        # 移除多余空白
        structure = re.sub(r'\s+', ' ', structure)
        # 截断过长的结构
        if len(structure) > 500:
            structure = structure[:500] + '...'
        return structure
    
    def _generate_report(self):
        """生成Markdown报告"""
        report = []
        
        # 标题
        report.append("# HRM2-Django-Backend API分析报告\n")
        report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("---\n")
        
        # 响应类型统计总结
        report.append("## 一、响应类型使用统计\n")
        report.append(self._generate_response_type_summary())
        
        # 响应格式一致性问题
        report.append("\n## 二、响应格式一致性分析\n")
        report.append(self._generate_consistency_analysis())
        
        # 按模块分类的API详情
        report.append("\n## 三、API详情\n")
        
        # 按模块分组
        modules = {}
        for api in self.apis:
            module = api['module']
            if module not in modules:
                modules[module] = []
            modules[module].append(api)
        
        for module_name, apis in modules.items():
            report.append(f"\n### 3.{list(modules.keys()).index(module_name)+1} {self._get_module_title(module_name)}\n")
            
            for api in apis:
                report.append(self._format_api_detail(api))
        
        # 保存报告
        report_content = '\n'.join(report)
        report_file = self.docs_path / 'API分析报告.md'
        report_file.write_text(report_content, encoding='utf-8')
        
        return report_content
    
    def _generate_response_type_summary(self) -> str:
        """生成响应类型统计总结"""
        lines = []
        
        # 统计各种响应类型
        type_stats = {
            'JsonResponse': {'files': set(), 'count': 0},
            'Response': {'files': set(), 'count': 0},
            'APIResponse': {'files': set(), 'count': 0},
            'FileResponse': {'files': set(), 'count': 0}
        }
        
        for api in self.apis:
            for resp_type, info in api['response_types'].items():
                if info['used']:
                    type_stats[resp_type]['files'].add(f"{api['module']}/{api['file']}")
                    type_stats[resp_type]['count'] += info['count']
        
        lines.append("| 响应类型 | 使用次数 | 涉及文件数 |")
        lines.append("|---------|---------|-----------|")
        
        for resp_type, stats in type_stats.items():
            if stats['count'] > 0:
                lines.append(f"| `{resp_type}` | {stats['count']} | {len(stats['files'])} |")
        
        lines.append("\n### 各文件使用的响应类型\n")
        
        file_types = {}
        for api in self.apis:
            key = f"{api['module']}/{api['file']}"
            if key not in file_types:
                file_types[key] = set()
            for resp_type, info in api['response_types'].items():
                if info['used']:
                    file_types[key].add(resp_type)
        
        lines.append("| 文件 | 使用的响应类型 |")
        lines.append("|------|---------------|")
        for file_path, types in sorted(file_types.items()):
            types_str = ', '.join(f'`{t}`' for t in sorted(types))
            lines.append(f"| `{file_path}` | {types_str} |")
        
        return '\n'.join(lines)
    
    def _generate_consistency_analysis(self) -> str:
        """生成一致性分析"""
        lines = []
        
        lines.append("### 发现的不一致问题\n")
        
        issues = []
        
        # 检查混合使用问题
        for api in self.apis:
            types_used = [t for t, info in api['response_types'].items() if info['used']]
            if len(types_used) > 1:
                issues.append({
                    'type': '混合响应类型',
                    'location': f"`{api['module']}/{api['file']}` - `{api['class_name']}`",
                    'detail': f"同时使用了: {', '.join(f'`{t}`' for t in types_used)}"
                })
        
        # 检查响应结构格式
        format_patterns = {
            'status_pattern': r"['\"]status['\"]:\s*['\"]success['\"]",
            'code_pattern': r"['\"]code['\"]:\s*200",
        }
        
        for api in self.apis:
            for resp in api.get('responses', []):
                structure = resp.get('structure', '')
                has_status = bool(re.search(format_patterns['status_pattern'], structure))
                has_code = bool(re.search(format_patterns['code_pattern'], structure))
                
                if has_status:
                    resp['format'] = 'status格式'
                elif has_code:
                    resp['format'] = 'code格式'
                else:
                    resp['format'] = '其他格式'
        
        if issues:
            lines.append("| 问题类型 | 位置 | 详情 |")
            lines.append("|---------|------|-----|")
            for issue in issues:
                lines.append(f"| {issue['type']} | {issue['location']} | {issue['detail']} |")
        else:
            lines.append("未发现明显的不一致问题。")
        
        # 响应格式分类
        lines.append("\n### 响应格式分类\n")
        lines.append("项目中使用了以下几种响应格式：\n")
        
        lines.append("#### 1. `status` 格式 (JsonResponse)\n")
        lines.append("```json")
        lines.append('{')
        lines.append('    "status": "success",')
        lines.append('    "message": "操作成功",')
        lines.append('    "data": { ... }')
        lines.append('}')
        lines.append("```\n")
        
        lines.append("#### 2. `code` 格式 (JsonResponse/APIResponse)\n")
        lines.append("```json")
        lines.append('{')
        lines.append('    "code": 200,')
        lines.append('    "message": "成功",')
        lines.append('    "data": { ... }')
        lines.append('}')
        lines.append("```\n")
        
        lines.append("#### 3. 直接数据格式 (JsonResponse/Response)\n")
        lines.append("```json")
        lines.append('{')
        lines.append('    "video_id": "xxx",')
        lines.append('    "status": "completed",')
        lines.append('    ... // 直接返回数据字段')
        lines.append('}')
        lines.append("```\n")
        
        lines.append("#### 4. 分页列表格式\n")
        lines.append("```json")
        lines.append('{')
        lines.append('    "results/tasks/videos/groups": [ ... ],')
        lines.append('    "total": 100,')
        lines.append('    "page": 1,')
        lines.append('    "page_size": 10')
        lines.append('}')
        lines.append("```\n")
        
        return '\n'.join(lines)
    
    def _get_module_title(self, module_name: str) -> str:
        """获取模块中文标题"""
        titles = {
            'position_settings': '岗位设置 (position_settings)',
            'resume_screening': '简历筛选 (resume_screening)',
            'video_analysis': '视频分析 (video_analysis)',
            'final_recommend': '最终推荐 (final_recommend)',
            'interview_assist': '面试辅助 (interview_assist)'
        }
        return titles.get(module_name, module_name)
    
    def _format_api_detail(self, api: dict) -> str:
        """格式化API详情"""
        lines = []
        
        lines.append(f"\n#### {api['class_name']}\n")
        
        if api['docstring']:
            lines.append(f"**描述**: {api['docstring']}\n")
        
        # 路由信息
        if api.get('route'):
            route = api['route']
            prefix = self._get_module_prefix(api['module'])
            full_path = f"/{prefix}/{route['path']}"
            lines.append(f"**路径**: `{full_path}`\n")
        
        # HTTP方法
        if api['methods']:
            lines.append("**支持的方法**:\n")
            for method in api['methods']:
                lines.append(f"- `{method['http_method']}`: {method['docstring'] or '无描述'}")
                if method['url_params']:
                    lines.append(f"  - URL参数: `{method['url_params']}`")
            lines.append("")
        
        # 请求参数
        if api['request_params']:
            lines.append("**请求参数**:\n")
            lines.append("| 参数名 | 必填 | 来源 | 默认值 |")
            lines.append("|-------|------|------|--------|")
            for param in api['request_params']:
                required = '是' if param.get('required') else '否'
                source = param.get('source', 'request.data')
                default = param.get('default', '-')
                if default and default != '-':
                    default = f"`{default}`"
                lines.append(f"| `{param['name']}` | {required} | {source} | {default} |")
            lines.append("")
        
        # 响应类型
        types_used = [t for t, info in api['response_types'].items() if info['used']]
        if types_used:
            lines.append(f"**响应类型**: {', '.join(f'`{t}`' for t in types_used)}\n")
        
        # 响应结构示例
        if api['responses']:
            lines.append("**响应结构示例**:\n")
            seen_structures = set()
            for resp in api['responses'][:3]:  # 只显示前3个
                if resp['type'] == 'APIResponse':
                    lines.append(f"- `APIResponse.{resp.get('method', 'unknown')}()`")
                else:
                    structure = resp.get('structure', '')
                    if structure and structure not in seen_structures:
                        seen_structures.add(structure)
                        # 格式化JSON结构
                        formatted = self._format_json_structure(structure)
                        lines.append(f"```json\n{formatted}\n```")
            lines.append("")
        
        lines.append("---\n")
        
        return '\n'.join(lines)
    
    def _get_module_prefix(self, module_name: str) -> str:
        """获取模块URL前缀"""
        prefixes = {
            'position_settings': 'position-settings',
            'resume_screening': 'resume-screening',
            'video_analysis': 'video-analysis',
            'final_recommend': 'final-recommend',
            'interview_assist': 'interview-assist'
        }
        return prefixes.get(module_name, module_name)
    
    def _format_json_structure(self, structure: str) -> str:
        """格式化JSON结构"""
        # 尝试美化JSON
        try:
            # 替换Python格式为JSON格式
            structure = structure.replace("'", '"')
            structure = re.sub(r'(\w+):', r'"\1":', structure)
            # 简单缩进
            level = 0
            result = []
            for char in structure:
                if char == '{':
                    result.append(char)
                    level += 1
                    result.append('\n' + '    ' * level)
                elif char == '}':
                    level -= 1
                    result.append('\n' + '    ' * level + char)
                elif char == ',':
                    result.append(char)
                    result.append('\n' + '    ' * level)
                else:
                    result.append(char)
            return ''.join(result)
        except:
            return structure


def main():
    """主函数"""
    # 获取项目根目录 (脚本在Docs目录下，需要向上一级)
    base_path = Path(__file__).parent.parent
    
    # 创建分析器并执行
    analyzer = APIAnalyzer(str(base_path))
    analyzer.analyze()


if __name__ == '__main__':
    main()
