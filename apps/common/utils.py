"""
通用工具函数模块。
"""
import hashlib
import json
import os
import re
from typing import Any, Dict
from datetime import datetime


def generate_hash(content: str) -> str:
    """生成内容的SHA256哈希值。"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def safe_json_loads(content: str, default: Any = None) -> Any:
    """安全加载JSON字符串。"""
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, **kwargs) -> str:
    """安全将数据转换为JSON字符串。"""
    try:
        return json.dumps(data, ensure_ascii=False, **kwargs)
    except (TypeError, ValueError):
        return "{}"


def sanitize_filename(filename: str) -> str:
    """通过移除/替换无效字符来清理文件名。"""
    # 移除无效字符
    sanitized = re.sub(r'[\\/:*?"<>|]', '_', filename)
    # 移除首尾空格和点号
    sanitized = sanitized.strip(' .')
    return sanitized or 'unnamed'


def get_timestamp_filename(prefix: str, suffix: str = '.md') -> str:
    """生成带时间戳的文件名。"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}{suffix}"


def ensure_dir(path: str) -> str:
    """确保目录存在并返回路径。"""
    os.makedirs(path, exist_ok=True)
    return path


def extract_name_from_filename(filename: str) -> str:
    """从文件名中提取名称（不含扩展名）。"""
    return os.path.splitext(os.path.basename(filename))[0]


def truncate_text(text: str, max_length: int = 500, suffix: str = '...') -> str:
    """将文本截断到指定长度。"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def dict_to_sorted_json(data: Dict) -> str:
    """将字典转换为排序后的JSON字符串，用于一致性哈希。"""
    return json.dumps(data, sort_keys=True, ensure_ascii=False)


def calculate_position_hash(position_title: str, position_details: Dict) -> str:
    """计算岗位信息的哈希值以确保一致性。"""
    position_str = dict_to_sorted_json({
        "position_title": position_title,
        "position_details": position_details
    })
    return generate_hash(position_str)
