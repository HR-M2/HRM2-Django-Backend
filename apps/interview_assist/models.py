"""
面试辅助数据模型模块。

数据库简化重构：
- InterviewAssistSession -> InterviewSession (重命名)
- 关联到新的 Resume 模型
- 删除 job_config（从 resume.position 获取）
- 删除 report_file（报告存JSON）
"""
from django.db import models
from django.utils import timezone
import uuid


class InterviewSession(models.Model):
    """
    面试辅助会话模型 - 简化版
    
    删除的字段:
    - job_config: 从 resume.position 获取岗位配置
    - report_file: 报告直接存JSON
    
    qa_records JSON 格式:
    [
        {
            "round": 1,
            "question": "问题内容",
            "answer": "回答内容",
            "evaluation": {...}
        }
    ]
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 关联简历
    resume = models.ForeignKey(
        'resume.Resume',
        on_delete=models.CASCADE,
        related_name='interview_sessions',
        verbose_name="简历"
    )
    
    # 问答记录（JSON数组）
    qa_records = models.JSONField(default=list, verbose_name="问答记录")
    
    # 最终报告
    final_report = models.JSONField(null=True, blank=True, verbose_name="面试报告")
    
    class Meta:
        db_table = 'interview_sessions'
        ordering = ['-created_at']
        verbose_name = "面试会话"
        verbose_name_plural = "面试会话"
    
    def __str__(self):
        candidate_name = self.resume.candidate_name if self.resume else "未知"
        status = "已完成" if self.is_completed else "进行中"
        return f"面试会话 - {candidate_name} ({status})"
    
    @property
    def current_round(self) -> int:
        """当前轮次 = 问答记录数量"""
        return len(self.qa_records) if self.qa_records else 0
    
    @property
    def is_completed(self) -> bool:
        """是否已完成（有最终报告即为完成）"""
        return self.final_report is not None
    
    @property
    def job_config(self) -> dict:
        """从关联简历获取岗位配置（兼容旧API）。"""
        if self.resume and self.resume.position:
            return self.resume.position.to_dict()
        return {}
    
    def add_qa_record(self, question: str, answer: str, evaluation: dict = None):
        """添加一条问答记录"""
        if self.qa_records is None:
            self.qa_records = []
        self.qa_records.append({
            "round": len(self.qa_records) + 1,
            "question": question,
            "answer": answer,
            "evaluation": evaluation
        })
        self.save(update_fields=['qa_records', 'updated_at'])
    
    def set_final_report(self, report: dict):
        """设置最终报告。"""
        self.final_report = report
        # 同时更新简历状态
        if self.resume:
            self.resume.update_status('interviewing')
        self.save(update_fields=['final_report', 'updated_at'])


# 保留旧模型别名以便于渐进式迁移（将在 Phase 8 删除）
InterviewAssistSession = InterviewSession
