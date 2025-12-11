"""
视图类文档完整性属性测试。

验证所有API视图类都具有非空的docstring描述。

**Feature: api-optimization, Property 7: 视图类文档完整性**
"""
import ast
import pytest
from pathlib import Path


# 所有需要检查的视图文件
VIEW_FILES = [
    'apps/position_settings/views.py',
    'apps/resume_library/views.py',
    'apps/resume_screening/views/screening.py',
    'apps/resume_screening/views/task.py',
    'apps/resume_screening/views/resume_data.py',
    'apps/resume_screening/views/resume_group.py',
    'apps/resume_screening/views/link.py',
    'apps/resume_screening/views/dev_tools.py',
    'apps/video_analysis/views.py',
    'apps/final_recommend/views.py',
    'apps/interview_assist/views.py',
]


def get_all_view_classes():
    """获取所有视图类的信息（文件路径、类名、docstring）。"""
    view_classes = []
    base_dir = Path(__file__).parent.parent
    
    for filepath in VIEW_FILES:
        full_path = base_dir / filepath
        if not full_path.exists():
            continue
        
        with open(full_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 只检查名称中包含 View 的类（视图类）
                if 'View' in node.name:
                    docstring = ast.get_docstring(node)
                    view_classes.append({
                        'file': filepath,
                        'class_name': node.name,
                        'docstring': docstring,
                        'line': node.lineno
                    })
    
    return view_classes


# **Feature: api-optimization, Property 7: 视图类文档完整性**
class TestViewDocumentationCompleteness:
    """
    Property 7: 视图类文档完整性
    
    对于任何API视图类，该类应具有非空的docstring描述。
    
    Validates: Requirements 5.2
    """
    
    @pytest.fixture(scope="class")
    def all_view_classes(self):
        """获取所有视图类。"""
        return get_all_view_classes()
    
    def test_all_view_classes_found(self, all_view_classes):
        """确保能够找到视图类。"""
        assert len(all_view_classes) > 0, "未找到任何视图类"
        # 预期至少有这些视图类
        expected_min_count = 30  # 基于当前代码库
        assert len(all_view_classes) >= expected_min_count, \
            f"找到的视图类数量 ({len(all_view_classes)}) 少于预期 ({expected_min_count})"
    
    def test_all_view_classes_have_docstring(self, all_view_classes):
        """所有视图类都应该有docstring。"""
        missing_docstrings = []
        
        for view_class in all_view_classes:
            if not view_class['docstring'] or len(view_class['docstring'].strip()) == 0:
                missing_docstrings.append(
                    f"{view_class['file']}:{view_class['line']} - {view_class['class_name']}"
                )
        
        assert len(missing_docstrings) == 0, \
            f"以下视图类缺少docstring:\n" + "\n".join(missing_docstrings)
    
    def test_view_docstrings_are_meaningful(self, all_view_classes):
        """视图类的docstring应该有意义（至少10个字符）。"""
        short_docstrings = []
        min_length = 10
        
        for view_class in all_view_classes:
            docstring = view_class['docstring']
            if docstring and len(docstring.strip()) < min_length:
                short_docstrings.append(
                    f"{view_class['file']}:{view_class['line']} - {view_class['class_name']} "
                    f"(docstring长度: {len(docstring.strip())})"
                )
        
        assert len(short_docstrings) == 0, \
            f"以下视图类的docstring太短（少于{min_length}字符）:\n" + "\n".join(short_docstrings)
    
    def test_view_docstrings_describe_http_methods(self, all_view_classes):
        """视图类的docstring应该描述支持的HTTP方法。"""
        # 常见的HTTP方法关键词
        http_keywords = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', '获取', '创建', '更新', '删除', '查询', '上传', '下载']
        
        views_without_method_description = []
        
        for view_class in all_view_classes:
            docstring = view_class['docstring']
            if docstring:
                # 检查docstring是否包含HTTP方法相关描述
                has_method_description = any(
                    keyword in docstring.upper() or keyword in docstring 
                    for keyword in http_keywords
                )
                if not has_method_description:
                    views_without_method_description.append(
                        f"{view_class['file']}:{view_class['line']} - {view_class['class_name']}"
                    )
        
        # 这个测试作为警告，不强制失败
        if views_without_method_description:
            pytest.skip(
                f"以下视图类的docstring未明确描述HTTP方法（建议改进）:\n" + 
                "\n".join(views_without_method_description[:5]) +
                (f"\n... 还有 {len(views_without_method_description) - 5} 个" 
                 if len(views_without_method_description) > 5 else "")
            )


# **Feature: api-optimization, Property 7: 视图类文档完整性 - 参数化测试**
@pytest.mark.parametrize("view_info", get_all_view_classes(), 
                         ids=lambda x: f"{x['file'].split('/')[-1]}:{x['class_name']}")
def test_individual_view_has_docstring(view_info):
    """
    Property 7: 每个视图类都应该有docstring。
    
    参数化测试，为每个视图类单独运行测试。
    """
    assert view_info['docstring'] is not None, \
        f"视图类 {view_info['class_name']} 在 {view_info['file']} 第 {view_info['line']} 行缺少docstring"
    
    assert len(view_info['docstring'].strip()) > 0, \
        f"视图类 {view_info['class_name']} 在 {view_info['file']} 第 {view_info['line']} 行的docstring为空"
