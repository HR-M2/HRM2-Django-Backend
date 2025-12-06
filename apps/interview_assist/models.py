"""
面试辅助数据模型模块（精简版）。

只保留一个模型 InterviewAssistSession，问答记录以 JSON 形式存储。
"""
from django.db import models
from django.utils import timezone
import uuid


class InterviewAssistSession(models.Model):
    """
    面试辅助会话模型（精简版）
    
    qa_records JSON 格式:
    [
        {
            "round": 1,
            "question": "问题内容",
            "answer": "回答内容",
            "evaluation": {...}  # AI评估结果
        },
        ...
    ]
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 关联简历
    resume_data = models.ForeignKey(
        'resume_screening.ResumeData',
        on_delete=models.CASCADE,
        related_name='interview_sessions',
        verbose_name="关联简历"
    )
    
    # 岗位配置（用于生成问题）
    job_config = models.JSONField(default=dict, verbose_name="岗位配置")
    
    # 问答记录（JSON数组）
    qa_records = models.JSONField(default=list, verbose_name="问答记录")
    
    # 最终报告
    final_report = models.JSONField(null=True, blank=True, verbose_name="最终报告")
    report_file = models.FileField(
        upload_to='interview_assist_reports/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name="报告文件"
    )
    
    @property
    def current_round(self) -> int:
        """当前轮次 = 问答记录数量"""
        return len(self.qa_records) if self.qa_records else 0
    
    @property
    def is_completed(self) -> bool:
        """是否已完成（有最终报告即为完成）"""
        return self.final_report is not None
    
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
    
    def __str__(self):
        candidate_name = self.resume_data.candidate_name if self.resume_data else "未知"
        status = "已完成" if self.is_completed else "进行中"
        return f"面试会话 - {candidate_name} ({status})"
    
    class Meta:
        db_table = 'interview_assist_sessions'
        ordering = ['-created_at']
        verbose_name = "面试辅助会话"
        verbose_name_plural = "面试辅助会话"
