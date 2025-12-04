#!/usr/bin/env python
"""Django管理任务的命令行工具。"""
import os
import sys


def main():
    """运行管理任务。"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入Django。请确保已安装Django并且"
            "在PYTHONPATH环境变量中可用。是否忘记"
            "激活虚拟环境？"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
