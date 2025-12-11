# Generated manually
# 将 ResumeLibrary 模型管理权转移到 resume_library 应用

from django.db import migrations


class Migration(migrations.Migration):
    """
    从 resume_screening 应用的状态中移除 ResumeLibrary 模型。
    
    使用 SeparateDatabaseAndState 确保：
    - 数据库表不会被删除（由 resume_library 应用继续管理）
    - Django 状态更新为本应用不再管理该模型
    """

    dependencies = [
        ('resume_screening', '0002_resumelibrary'),
        # 确保 resume_library 先创建状态
        ('resume_library', '0001_initial'),
    ]

    operations = [
        # 使用 SeparateDatabaseAndState：只更新 Django 状态，不执行数据库操作
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # 从状态中删除模型
                migrations.DeleteModel(
                    name='ResumeLibrary',
                ),
            ],
            database_operations=[],  # 不执行任何数据库操作，表由 resume_library 管理
        ),
    ]
