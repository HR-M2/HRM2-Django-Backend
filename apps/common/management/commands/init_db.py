"""
数据库初始化命令。

用法:
    python manage.py init_db          # 创建迁移并应用
    python manage.py init_db --fresh  # 删除旧迁移，重新创建并应用
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings


class Command(BaseCommand):
    help = '一键初始化数据库：创建所有应用的迁移文件并应用到数据库'

    # 需要创建迁移的应用列表
    APP_LIST = [
        'position_settings',
        'resume_screening', 
        'video_analysis',
        'interview_assist',
        'final_recommend',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--fresh',
            action='store_true',
            help='删除现有迁移文件，重新生成（谨慎使用，会丢失迁移历史）',
        )
        parser.add_argument(
            '--no-migrate',
            action='store_true',
            help='仅创建迁移文件，不应用到数据库',
        )

    def handle(self, *args, **options):
        fresh = options.get('fresh', False)
        no_migrate = options.get('no_migrate', False)

        self.stdout.write(self.style.NOTICE('=' * 50))
        self.stdout.write(self.style.NOTICE('开始数据库初始化...'))
        self.stdout.write(self.style.NOTICE('=' * 50))

        # 如果指定了 --fresh，先删除现有迁移文件
        if fresh:
            self.stdout.write(self.style.WARNING('\n⚠️  正在删除现有迁移文件...'))
            self._delete_migrations()

        # 创建迁移文件
        self.stdout.write(self.style.NOTICE('\n📝 正在创建迁移文件...'))
        try:
            call_command('makemigrations', *self.APP_LIST, verbosity=1)
            self.stdout.write(self.style.SUCCESS('✅ 迁移文件创建完成'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ 创建迁移文件失败: {e}'))
            return

        # 应用迁移
        if not no_migrate:
            self.stdout.write(self.style.NOTICE('\n🚀 正在应用迁移到数据库...'))
            try:
                call_command('migrate', verbosity=1)
                self.stdout.write(self.style.SUCCESS('✅ 数据库迁移完成'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ 数据库迁移失败: {e}'))
                return

        # 完成
        self.stdout.write(self.style.NOTICE('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('🎉 数据库初始化完成！'))
        self.stdout.write(self.style.NOTICE('=' * 50))

        # 显示表信息
        self._show_tables_info()

    def _delete_migrations(self):
        """删除所有应用的迁移文件（保留 __init__.py）"""
        apps_dir = os.path.join(settings.BASE_DIR, 'apps')
        
        for app_name in self.APP_LIST:
            migrations_dir = os.path.join(apps_dir, app_name, 'migrations')
            
            if os.path.exists(migrations_dir):
                for filename in os.listdir(migrations_dir):
                    if filename != '__init__.py' and filename != '__pycache__':
                        file_path = os.path.join(migrations_dir, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            self.stdout.write(f'  删除: {app_name}/migrations/{filename}')
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                            self.stdout.write(f'  删除目录: {app_name}/migrations/{filename}')

    def _show_tables_info(self):
        """显示已创建的表信息"""
        from django.db import connection
        
        self.stdout.write(self.style.NOTICE('\n📊 数据库表信息:'))
        
        with connection.cursor() as cursor:
            # 获取所有表名（SQLite）
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = cursor.fetchall()
            
            app_tables = [t[0] for t in tables if not t[0].startswith('django_') 
                         and not t[0].startswith('auth_') 
                         and not t[0].startswith('sqlite_')
                         and t[0] != 'django_migrations']
            
            if app_tables:
                for table in app_tables:
                    self.stdout.write(f'  ✓ {table}')
            else:
                self.stdout.write('  (无应用表)')
