#!/usr/bin/env python
"""
HRM2-Django-Backend 一键启动脚本
支持自动检测环境、检查依赖、启动服务器
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 环境配置映射
SETTINGS_MAP = {
    'dev': 'config.settings.development',
    'development': 'config.settings.development',
    'prod': 'config.settings.production',
    'production': 'config.settings.production',
    'test': 'config.settings.testing',
    'testing': 'config.settings.testing',
}


def print_banner():
    """打印启动横幅"""
    print("\n" + "=" * 50)
    print("  HRM2-Django-Backend 启动器")
    print("=" * 50)


def check_env_file():
    """检查 .env 文件是否存在"""
    env_file = BASE_DIR / '.env'
    env_example = BASE_DIR / '.env.example'
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  未找到 .env 文件")
            print(f"   请复制 .env.example 并配置: cp .env.example .env")
            return False
        else:
            print("⚠️  未找到 .env 和 .env.example 文件")
            return False
    
    print("✅ 找到 .env 配置文件")
    return True


def check_dependencies():
    """检查关键依赖是否已安装"""
    required = ['django', 'rest_framework']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  缺少依赖: {', '.join(missing)}")
        print("   请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 依赖检查通过")
    return True


def run_migrations(settings_module):
    """运行数据库迁移"""
    print("\n📦 检查数据库迁移...")
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    
    try:
        result = subprocess.run(
            [sys.executable, 'manage.py', 'migrate', '--check'],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        
        if result.returncode != 0:
            print("   发现未应用的迁移，正在执行...")
            subprocess.run(
                [sys.executable, 'manage.py', 'migrate'],
                cwd=BASE_DIR
            )
        else:
            print("✅ 数据库已是最新状态")
    except Exception as e:
        print(f"⚠️  迁移检查失败: {e}")


def generate_api_docs():
    """生成 API 文档"""
    print("\n📄 生成 API 文档...")
    docs_script = BASE_DIR / 'Docs' / '生成API文档.py'
    
    if not docs_script.exists():
        print("   ⚠️ 未找到文档生成脚本，跳过")
        return
    
    try:
        result = subprocess.run(
            [sys.executable, str(docs_script)],
            capture_output=True,
            text=True,
            cwd=BASE_DIR / 'Docs'
        )
        
        if result.returncode == 0:
            # 从输出中提取端点数量
            for line in result.stdout.split('\n'):
                if 'API端点' in line:
                    print(f"✅ {line.strip()}")
                    break
            else:
                print("✅ API 文档已更新")
        else:
            print(f"   ⚠️ 生成失败: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️ 生成失败: {e}")


def start_server(host, port, settings_module, no_reload=False):
    """启动 Django 开发服务器"""
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
    
    print(f"\n🚀 启动服务器...")
    print(f"   环境: {settings_module}")
    print(f"   地址: http://{host}:{port}/")
    print(f"   API文档: http://{host}:{port}/api/")
    print("\n   按 Ctrl+C 停止服务器\n")
    print("-" * 50)
    
    cmd = [sys.executable, 'manage.py', 'runserver', f'{host}:{port}']
    if no_reload:
        cmd.append('--noreload')
    
    try:
        subprocess.run(cmd, cwd=BASE_DIR)
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='HRM2-Django-Backend 一键启动脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run.py                    # 使用默认配置启动 (development, 8000端口)
  python run.py -p 8080            # 指定端口 8080
  python run.py -e prod            # 使用生产环境配置
  python run.py --host 0.0.0.0     # 允许外部访问
  python run.py --skip-checks      # 跳过依赖和迁移检查
        """
    )
    
    parser.add_argument(
        '-e', '--env',
        choices=['dev', 'development', 'prod', 'production', 'test', 'testing'],
        default='dev',
        help='运行环境 (默认: dev)'
    )
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=8000,
        help='服务器端口 (默认: 8000)'
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='服务器地址 (默认: 127.0.0.1)'
    )
    parser.add_argument(
        '--no-reload',
        action='store_true',
        help='禁用自动重载'
    )
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='跳过依赖和迁移检查'
    )
    parser.add_argument(
        '--migrate-only',
        action='store_true',
        help='仅运行迁移，不启动服务器'
    )
    
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    # 获取设置模块
    settings_module = SETTINGS_MAP[args.env]
    print(f"\n📍 当前环境: {args.env}")
    
    # 检查
    if not args.skip_checks:
        if not check_env_file():
            sys.exit(1)
        
        if not check_dependencies():
            sys.exit(1)
        
        run_migrations(settings_module)
        
        generate_api_docs()
    
    # 仅迁移模式
    if args.migrate_only:
        print("\n✅ 迁移完成")
        sys.exit(0)
    
    # 启动服务器
    start_server(args.host, args.port, settings_module, args.no_reload)


if __name__ == '__main__':
    main()
