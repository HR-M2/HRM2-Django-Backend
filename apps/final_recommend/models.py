"""
最终推荐数据模型模块。

数据库简化重构：
- CandidateComprehensiveAnalysis -> ComprehensiveAnalysis (重命名+简化)
- 合并 recommendation_level/label/action 到 recommendation JSON
- 删除 input_data_snapshot
- 删除废弃的 InterviewEvaluationTask 模型
"""
from django.db import models
from django.utils import timezone
import uuid


class ComprehensiveAnalysis(models.Model):
    """
    综合分析结果模型 - 简化版
    
    删除的字段:
    - recommendation_level/label/action: 合并到 recommendation JSON
    - input_data_snapshot: 可从关联表获取，不再冗余存储
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    
    # 关联简历
    resume = models.ForeignKey(
        'resume.Resume',
        on_delete=models.CASCADE,
        related_name='comprehensive_analyses',
        verbose_name="简历"
    )
    
    # 评估结果
    final_score = models.FloatField(verbose_name="综合得分")
    
    # 推荐结果（JSON合并）
    recommendation = models.JSONField(verbose_name="推荐结果")
    # 格式示例:
    # {
    #     "level": "A",
    #     "label": "强烈推荐",
    #     "action": "建议尽快发放offer"
    # }
    
    # 维度评分
    dimension_scores = models.JSONField(default=dict, verbose_name="维度评分")
    
    # 综合报告
    report = models.TextField(verbose_name="综合报告")
    
    class Meta:
        db_table = 'comprehensive_analyses'
        ordering = ['-created_at']
        verbose_name = "综合分析"
        verbose_name_plural = "综合分析"
    
    def __str__(self):
        label = self.recommendation.get('label', '未知') if self.recommendation else '未知'
        return f"{self.resume.candidate_name} 综合分析 ({label})"
    
    @property
    def recommendation_level(self):
        """兼容旧API。"""
        return self.recommendation.get('level', '') if self.recommendation else ''
    
    @property
    def recommendation_label(self):
        """兼容旧API。"""
        return self.recommendation.get('label', '') if self.recommendation else ''
    
    @property
    def recommendation_action(self):
        """兼容旧API。"""
        return self.recommendation.get('action', '') if self.recommendation else ''
    
    @property
    def comprehensive_report(self):
        """兼容旧字段名。"""
        return self.report
    
    def set_result(self, score: float, recommendation: dict, dimension_scores: dict, report: str):
        """设置分析结果并更新简历状态。"""
        self.final_score = score
        self.recommendation = recommendation
        self.dimension_scores = dimension_scores
        self.report = report
        self.save()
        # 更新简历状态
        if self.resume:
            self.resume.update_status('analyzed')


