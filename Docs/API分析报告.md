# HRM2-Django-Backend API分析报告

**生成时间**: 2025-12-05 12:00:00

---

## 一、响应类型使用统计

| 响应类型 | 使用次数 | 涉及文件数 |
|---------|---------|-----------|
| `JsonResponse` | 76 | 8 |
| `Response` | 50 | 5 |
| `FileResponse` | 2 | 1 |

### 各文件使用的响应类型

| 文件 | 使用的响应类型 |
|------|---------------|
| `final_recommend/views.py` | `FileResponse`, `JsonResponse` |
| `interview_assist/views.py` | `JsonResponse` |
| `position_settings/views.py` | `JsonResponse` |
| `resume_screening/link.py` | `Response` |
| `resume_screening/resume_data.py` | `JsonResponse`, `Response` |
| `resume_screening/resume_group.py` | `JsonResponse`, `Response` |
| `resume_screening/screening.py` | `JsonResponse`, `Response` |
| `resume_screening/task.py` | `JsonResponse` |
| `video_analysis/views.py` | `JsonResponse`, `Response` |

## 二、响应格式一致性分析

### 发现的不一致问题

| 问题类型 | 位置 | 详情 |
|---------|------|-----|
| 混合响应类型 | `resume_screening/resume_data.py` - `ResumeDataView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `resume_screening/resume_data.py` - `ResumeDataDetailView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `resume_screening/resume_group.py` - `ResumeGroupListView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `resume_screening/resume_group.py` - `ResumeGroupDetailView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `resume_screening/resume_group.py` - `CreateResumeGroupView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `resume_screening/resume_group.py` - `AddResumeToGroupView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `resume_screening/resume_group.py` - `RemoveResumeFromGroupView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `resume_screening/resume_group.py` - `SetGroupStatusView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `resume_screening/screening.py` - `ResumeScreeningView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `resume_screening/screening.py` - `ScreeningTaskStatusView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `video_analysis/views.py` - `VideoAnalysisView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `video_analysis/views.py` - `VideoAnalysisStatusView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `video_analysis/views.py` - `VideoAnalysisUpdateView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `video_analysis/views.py` - `VideoAnalysisListView` | 同时使用了: `JsonResponse`, `Response` |
| 混合响应类型 | `final_recommend/views.py` - `InterviewEvaluationView` | 同时使用了: `JsonResponse`, `FileResponse` |
| 混合响应类型 | `final_recommend/views.py` - `ReportDownloadView` | 同时使用了: `JsonResponse`, `FileResponse` |

### 响应格式分类

项目中使用了以下几种响应格式：

#### 1. `status` 格式 (JsonResponse)

```json
{
    "status": "success",
    "message": "操作成功",
    "data": { ... }
}
```

#### 2. `code` 格式 (JsonResponse/APIResponse)

```json
{
    "code": 200,
    "message": "成功",
    "data": { ... }
}
```

#### 3. 直接数据格式 (JsonResponse/Response)

```json
{
    "video_id": "xxx",
    "status": "completed",
    ... // 直接返回数据字段
}
```

#### 4. 分页列表格式

```json
{
    "results/tasks/videos/groups": [ ... ],
    "total": 100,
    "page": 1,
    "page_size": 10
}
```


## 三、API详情


### 3.1 岗位设置 (position_settings)


#### RecruitmentCriteriaView

**描述**: 招聘标准API
    GET: 获取当前招聘标准
    POST: 更新招聘标准

**路径**: `/position-settings/`

**支持的方法**:

- `GET`: 获取招聘标准。
- `POST`: 更新招聘标准。

**响应类型**: `JsonResponse`

**响应结构示例**:

```json
{
    "code": 200,
     "message": "成功",
     "data": data
}
```
```json
{
    "code": 500,
     "message": "文件格式错误，非有效JSON"
}
```
```json
{
    "code": 500,
     "message": f""服务器内部错误": {
        str(e)
    }
```

---


#### PositionCriteriaListView

**描述**: 岗位标准列表API
    GET: 获取所有岗位标准列表

**路径**: `/position-settings/list/`

**支持的方法**:

- `GET`: 获取所有岗位标准。

**响应类型**: `JsonResponse`

**响应结构示例**:

```json
{
    "code": 200,
     "message": "成功",
     "data": data
}
```

---


### 3.2 简历筛选 (resume_screening)


#### LinkResumeVideoView

**描述**: 关联简历与视频API
    POST: 建立简历与视频分析的关联

**路径**: `/resume-screening/link-resume-to-video/`

**支持的方法**:

- `POST`: 将简历数据与视频分析关联。

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `resume_data_id` | 是 | request.data | None |
| `video_analysis_id` | 是 | request.data | None |

**响应类型**: `Response`

**响应结构示例**:

```json
{
     "message": "简历数据与视频分析记录关联成功",
     "resume_data_id": str(resume_data.id),
     "video_analysis_id": str(video_analysis.id),
     "candidate_name": resume_data.candidate_name,
     "video_name": video_analysis.video_name 
}
```

---


#### UnlinkResumeVideoView

**描述**: 解除简历与视频关联API
    POST: 解除简历与视频分析的关联

**路径**: `/resume-screening/unlink-resume-from-video/`

**支持的方法**:

- `POST`: 解除简历数据与视频分析的关联。

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `resume_data_id` | 是 | request.data | None |

**响应类型**: `Response`

**响应结构示例**:

```json
{
     "message": "简历数据与视频分析记录解除关联成功",
     "resume_data_id": str(resume_data.id),
     "disconnected_video_id": video_id,
     "candidate_name": resume_data.candidate_name,
     "video_name": video_name 
}
```

---


#### ResumeDataView

**描述**: 简历数据管理API
    GET: 获取简历数据列表
    POST: 创建新的简历数据

**路径**: `/resume-screening/data/`

**支持的方法**:

- `GET`: 获取简历数据列表，支持过滤和分页。
- `POST`: 创建新的简历数据记录。

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `position_title` | 是 | request.data | None |
| `position_details` | 否 | request.data | `{}` |
| `candidate_name` | 是 | request.data | None |
| `resume_content` | 是 | request.data | None |
| `page` | 否 | request.GET | - |
| `page_size` | 否 | request.GET | - |

**响应类型**: `JsonResponse`, `Response`

**响应结构示例**:

```json
{
     "results": result,
     "total": total,
     "page": page,
     "page_size": page_size 
}
```
```json
{
     "id": str(resume_data.id),
     "message": "简历数据创建成功" 
}
```

---


#### ResumeDataDetailView

**描述**: 简历数据详情API
    GET: 获取简历数据详情

**路径**: `/resume-screening/reports/<uuid:report_id>/detail/`

**支持的方法**:

- `GET`: 获取简历数据详情。
  - URL参数: `resume_id`

**响应类型**: `JsonResponse`, `Response`

**响应结构示例**:

```json
{
    "report": data
}
```

---


#### ResumeGroupListView

**描述**: 简历组列表API
    GET: 获取简历组列表

**路径**: `/resume-screening/groups/`

**支持的方法**:

- `GET`: 获取简历组列表，支持过滤和分页。

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `page` | 否 | request.GET | - |
| `page_size` | 否 | request.GET | - |
| `position_title` | 否 | request.GET | - |
| `status` | 否 | request.GET | - |
| `include_resumes` | 否 | request.GET | - |

**响应类型**: `JsonResponse`, `Response`

**响应结构示例**:

```json
{
     "groups": groups_data,
     "total": total,
     "page": page,
     "page_size": page_size 
}
```

---


#### ResumeGroupDetailView

**描述**: 简历组详情API
    GET: 获取简历组详情

**路径**: `/resume-screening/groups/<uuid:group_id>/`

**支持的方法**:

- `GET`: 获取简历组详情。
  - URL参数: `group_id`

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `include_resumes` | 否 | request.GET | - |

**响应类型**: `JsonResponse`, `Response`

**响应结构示例**:

```json
{
     "group": group_data,
     "summary": {
         "total_resumes": resume_count,
         "status": group.status,
         "created_at": group.created_at.isoformat() 
    }
```

---


#### CreateResumeGroupView

**描述**: 创建简历组API
    POST: 创建新的简历组

**路径**: `/resume-screening/groups/create/`

**支持的方法**:

- `POST`: 创建简历组。

**响应类型**: `JsonResponse`, `Response`

**响应结构示例**:

```json
{
    "error": "参数验证失败",
     "details": serializer.errors
}
```
```json
{
     "message": "简历组创建成功",
     "group_id": str(group.id),
     "group_name": group.group_name,
     "resume_count": group.resume_count 
}
```

---


#### AddResumeToGroupView

**描述**: 添加简历到组API
    POST: 向简历组添加简历

**路径**: `/resume-screening/groups/add-resume/`

**支持的方法**:

- `POST`: 向组中添加简历。

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `group_id` | 是 | request.data | None |
| `resume_data_id` | 是 | request.data | None |

**响应类型**: `JsonResponse`, `Response`

**响应结构示例**:

```json
{
     "message": "简历成功添加到简历组",
     "group_id": str(group.id),
     "group_name": group.group_name,
     "resume_count": group.resume_count 
}
```

---


#### RemoveResumeFromGroupView

**描述**: 从组中移除简历API
    POST: 从简历组移除简历

**路径**: `/resume-screening/groups/remove-resume/`

**支持的方法**:

- `POST`: 从组中移除简历。

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `group_id` | 是 | request.data | None |
| `resume_data_id` | 是 | request.data | None |

**响应类型**: `JsonResponse`, `Response`

**响应结构示例**:

```json
{
     "message": "简历成功从简历组中移除",
     "group_id": str(group.id),
     "group_name": group.group_name,
     "resume_count": group.resume_count 
}
```

---


#### SetGroupStatusView

**描述**: 设置简历组状态API
    POST: 更新简历组状态

**路径**: `/resume-screening/groups/set-status/`

**支持的方法**:

- `POST`: 设置组状态。

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `group_id` | 是 | request.data | None |
| `status` | 是 | request.data | None |

**响应类型**: `JsonResponse`, `Response`

**响应结构示例**:

```json
{
     "message": "简历组状态更新成功",
     "group_id": str(group.id),
     "group_name": group.group_name,
     "status": group.status 
}
```

---


#### ResumeScreeningView

**描述**: 简历初筛API
    POST: 提交简历筛选任务

**路径**: `/resume-screening/screening/`

**支持的方法**:

- `POST`: 提交简历筛选任务。

**响应类型**: `JsonResponse`, `Response`

**响应结构示例**:

```json
{
    "error": "参数验证失败",
     "details": serializer.errors
}
```
```json
{
     "status": "submitted",
     "message": "简历筛选任务已提交，正在后台处理",
     "task_id": str(task.id) 
}
```
```json
{
    "error": e.message,
     "details": e.errors
}
```

---


#### ScreeningTaskStatusView

**描述**: 查询筛选任务状态API
    GET: 获取任务状态和结果

**路径**: `/resume-screening/tasks/<uuid:task_id>/status/`

**支持的方法**:

- `GET`: 获取任务状态。
  - URL参数: `task_id`

**响应类型**: `JsonResponse`, `Response`

---


#### TaskHistoryView

**描述**: 任务历史API
    GET: 获取历史任务列表

**路径**: `/resume-screening/tasks-history/`

**支持的方法**:

- `GET`: 获取任务历史，支持分页。

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `page` | 否 | request.GET | - |
| `page_size` | 否 | request.GET | - |
| `status` | 否 | request.GET | - |

**响应类型**: `JsonResponse`

**响应结构示例**:

```json
{
     "tasks": result,
     "total": total,
     "page": page,
     "page_size": page_size 
}
```

---


#### ReportDownloadView

**描述**: 报告下载API
    GET: 下载筛选报告

**路径**: `/resume-screening/reports/<uuid:report_id>/download/`

**支持的方法**:

- `GET`: 下载筛选报告。
  - URL参数: `report_id`

**响应类型**: `JsonResponse`

---


### 3.3 视频分析 (video_analysis)


#### VideoAnalysisView

**描述**: 视频分析API
    POST: 上传视频并开始分析

**路径**: `/video-analysis/`

**支持的方法**:

- `POST`: 上传视频并开始分析。

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `candidate_name` | 是 | request.data | None |
| `position_applied` | 是 | request.data | None |
| `resume_data_id` | 否 | request.data | None |
| `video_name` | 否 | request.data | None |
| `video_file` | 否 | request.FILES | - |

**响应类型**: `JsonResponse`, `Response`

---


#### VideoAnalysisStatusView

**描述**: 视频分析状态API
    GET: 获取视频分析状态和结果

**路径**: `/video-analysis/<uuid:video_id>/status/`

**支持的方法**:

- `GET`: 获取视频分析状态。
  - URL参数: `video_id`

**响应类型**: `JsonResponse`, `Response`

---


#### VideoAnalysisUpdateView

**描述**: 视频分析结果更新API
    POST: 更新视频分析结果

**路径**: `/video-analysis/<uuid:video_id>/update/`

**支持的方法**:

- `POST`: 更新视频分析结果。
  - URL参数: `video_id`

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `fraud_score` | 否 | request.data | - |
| `neuroticism_score` | 否 | request.data | - |
| `extraversion_score` | 否 | request.data | - |
| `openness_score` | 否 | request.data | - |
| `agreeableness_score` | 否 | request.data | - |
| `conscientiousness_score` | 否 | request.data | - |
| `summary` | 否 | request.data | - |
| `confidence_score` | 否 | request.data | - |
| `status` | 否 | request.data | - |

**响应类型**: `JsonResponse`, `Response`

---


#### VideoAnalysisListView

**描述**: 视频分析列表API
    GET: 获取视频分析列表

**路径**: `/video-analysis/list/`

**支持的方法**:

- `GET`: 获取视频分析列表，支持过滤和分页。

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `candidate_name` | 否 | request.GET | - |
| `position_applied` | 否 | request.GET | - |
| `status` | 否 | request.GET | - |

**响应类型**: `JsonResponse`, `Response`

**响应结构示例**:

```json
{
     "videos": result,
     "total": pagination["total"],
     "page": pagination["page"],
     "page_size": pagination["page_size"] 
}
```

---


### 3.4 最终推荐 (final_recommend)


#### InterviewEvaluationView

**描述**: 面试后评估API
    POST: 启动评估任务
    GET: 获取任务状态
    DELETE: 删除任务

**路径**: `/final-recommend/interview-evaluation/`

**支持的方法**:

- `POST`: 启动评估任务。
- `GET`: 获取任务状态。
  - URL参数: `task_id=None`
- `DELETE`: 删除任务。
  - URL参数: `task_id=None`

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `group_id` | 是 | request.data | None |

**响应类型**: `JsonResponse`, `FileResponse`

**响应结构示例**:

```json
{
     "status": "success",
     "message": "面试后评估任务已启动",
     "data": {
         "task_id": str(task.id),
         "status": task.status 
    }
```
```json
{
     "status": "success",
     "message": f"任务 {
        task_id
    }
```
```json
{
     "status": "success",
     "data": data 
}
```

---


#### ReportDownloadView

**描述**: 报告下载API
    GET: 下载评估报告

**路径**: `/final-recommend/download-report/<path:file_path>`

**支持的方法**:

- `GET`: 下载报告文件。
  - URL参数: `file_path`

**响应类型**: `JsonResponse`, `FileResponse`

---


### 3.5 面试辅助 (interview_assist)


#### SessionView

**描述**: 面试会话API
    POST: 创建会话
    GET: 获取会话详情
    DELETE: 结束会话

**路径**: `/interview-assist/sessions/`

**支持的方法**:

- `POST`: 创建面试会话。
- `GET`: 获取会话详情。
  - URL参数: `session_id=None`
- `DELETE`: 结束会话。
  - URL参数: `session_id=None`

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `resume_data_id` | 是 | request.data | None |
| `interviewer_name` | 否 | request.data | `'面试官'` |
| `job_config` | 否 | request.data | `{}` |
| `company_config` | 否 | request.data | `{}` |

**响应类型**: `JsonResponse`

**响应结构示例**:

```json
{
     "status": "success",
     "message": "面试辅助会话已创建",
     "data": {
         "session_id": str(session.id),
         "candidate_name": resume_data.candidate_name,
         "position_title": job_config.get("title",
         resume_data.position_title),
         "status": session.status,
         "created_at": session.created_at.isoformat(),
         "resume_summary": resume_summary 
    }
```
```json
{
     "status": "success",
     "data": response_data 
}
```
```json
{
     "status": "success",
     "message": "会话已结束" 
}
```

---


#### GenerateQuestionsView

**描述**: 生成问题API
    POST: 生成候选问题

**路径**: `/interview-assist/sessions/<uuid:session_id>/generate-questions/`

**支持的方法**:

- `POST`: 生成候选问题。
  - URL参数: `session_id`

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `categories` | 否 | request.data | `['简历相关', '专业能力', '行为面试']` |
| `candidate_level` | 否 | request.data | `'senior'` |
| `focus_on_resume` | 否 | request.data | `True` |
| `count_per_category` | 否 | request.data | - |

**响应类型**: `JsonResponse`

**响应结构示例**:

```json
{
     "status": "success",
     "message": f"已生成{
        len(all_questions)
    }
```

---


#### RecordQAView

**描述**: 记录问答API
    POST: 记录问答并获取评估

**路径**: `/interview-assist/sessions/<uuid:session_id>/record-qa/`

**支持的方法**:

- `POST`: 记录问答并获取评估。
  - URL参数: `session_id`

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `question` | 否 | request.data | `{}` |
| `answer` | 否 | request.data | `{}` |

**响应类型**: `JsonResponse`

**响应结构示例**:

```json
{
     "status": "success",
     "message": "问答已记录，评估完成",
     "data": {
         "round_number": round_number,
         "qa_record_id": str(qa_record.id),
         "evaluation": evaluation,
         "followup_recommendation": followup_recommendation,
         "hr_action_hints": hr_hints 
    }
```

---


#### GenerateReportView

**描述**: 生成报告API
    POST: 生成最终报告

**路径**: `/interview-assist/sessions/<uuid:session_id>/generate-report/`

**支持的方法**:

- `POST`: 生成最终报告。
  - URL参数: `session_id`

**请求参数**:

| 参数名 | 必填 | 来源 | 默认值 |
|-------|------|------|--------|
| `include_conversation_log` | 否 | request.data | `True` |
| `hr_notes` | 否 | request.data | `''` |

**响应类型**: `JsonResponse`

**响应结构示例**:

```json
{
     "status": "success",
     "message": "评估报告生成成功",
     "data": {
         "report": report,
         "report_file_url": session.report_file.url if session.report_file else None 
    }
```

---
