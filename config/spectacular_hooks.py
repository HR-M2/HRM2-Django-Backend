"""
drf-spectacular 钩子函数。
用于自动根据URL路径为API分配标签和过滤无关接口。
"""


def preprocess_exclude_path(endpoints):
    """
    预处理钩子：过滤掉非业务接口。
    """
    filtered = []
    
    for endpoint in endpoints:
        path = endpoint[0]
        # 跳过 admin 和 api/ 等非业务接口
        if path.startswith('/admin/') or path.startswith('/api/'):
            continue
        filtered.append(endpoint)
    
    return filtered


def custom_postprocessing_hook(result, generator, request, public):
    """
    后处理钩子：根据URL路径自动为操作分配标签。
    """
    # 标签映射
    tag_mapping = {
        '/position-settings/': 'position-settings',
        '/resume-screening/': 'resume-screening',
        '/video-analysis/': 'video-analysis',
        '/interview-assist/': 'interview-assist',
        '/final-recommend/': 'final-recommend',
    }
    
    paths = result.get('paths', {})
    for path, methods in paths.items():
        # 找到匹配的标签
        tag = None
        for prefix, tag_name in tag_mapping.items():
            if path.startswith(prefix):
                tag = tag_name
                break
        
        if tag:
            for method, operation in methods.items():
                if isinstance(operation, dict) and 'tags' not in operation:
                    operation['tags'] = [tag]
                elif isinstance(operation, dict) and not operation.get('tags'):
                    operation['tags'] = [tag]
    
    return result
