# API 变更日志

## 2025-12-11：废弃批量评估功能

### 移除的 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/final-recommend/interview-evaluation/` | POST | 创建批量评估任务 |
| `/final-recommend/interview-evaluation/<task_id>/` | GET | 获取任务状态 |
| `/final-recommend/interview-evaluation/?group_id=<id>` | GET | 按组ID查询任务 |
| `/final-recommend/interview-evaluation/<task_id>/delete/` | DELETE | 删除任务 |
| `/final-recommend/download-report/<path>` | GET | 下载评估报告 |

### 移除的后端组件

- `EvaluationAgentManager` 类
- `EvaluationService.run_evaluation()` 方法
- `InterviewEvaluationView` 视图
- `run_evaluation_task` Celery 任务

### 现用 API

**单人综合分析**

```
POST /final-recommend/comprehensive-analysis/<resume_id>/
```

请求体：无（使用路径参数 resume_id）

响应：
```json
{
  "status": "success",
  "data": {
    "final_score": 85,
    "recommendation_level": "strongly_recommend",
    "recommendation_label": "强烈推荐",
    "dimension_scores": {...},
    "full_report": "..."
  }
}
```

```
GET /final-recommend/comprehensive-analysis/<resume_id>/
```

返回该候选人的历史分析记录。

### 迁移指南

| 旧方式 | 新方式 |
|--------|--------|
| 批量评估多人 | 逐个调用单人综合分析 API |
| `recommendApi.createEvaluation(groupId)` | `recommendApi.analyzeCandidate(resumeId)` |
| `InterviewEvaluationTask` 类型 | `ComprehensiveAnalysisResult` 类型 |

### 数据库清理

`InterviewEvaluationTask` 模型已标记为废弃但暂时保留。如需彻底清理，可创建迁移删除 `interview_evaluation_tasks` 表：

```bash
python manage.py makemigrations final_recommend --name remove_interview_evaluation_task
python manage.py migrate
```
