"""
最终推荐的Celery任务模块。

注意: 批量评估任务（run_evaluation_task）已废弃并移除。
批量评估功能不再支持，请使用 CandidateComprehensiveAnalyzer 进行单人综合分析。
"""
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# run_evaluation_task 已废弃并删除
# 批量评估功能不再支持
# 如需对候选人进行综合分析，请使用:
#   - API: POST /final-recommend/comprehensive-analysis/{resume_id}/
#   - 服务: services.agents.CandidateComprehensiveAnalyzer
# ============================================================================
