# HRM2 后端 API 参考文档

> 自动生成于 2025-12-11 12:36:20

> 共 41 个API端点

---

## 目录

- [岗位设置](#position_settings)
- [简历筛选](#resume_screening)
- [视频分析](#video_analysis)
- [最终推荐](#final_recommend)
- [面试辅助](#interview_assist)
- [其他](#other)

---

## 岗位设置 {position_settings}

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/position-settings/` | 获取招聘标准。 |
| `POST` | `/position-settings/` | 更新招聘标准。 |
| `GET` | `/position-settings/positions/` | 获取所有岗位标准。 |
| `POST` | `/position-settings/positions/` | 创建新岗位。 |
| `GET` | `/position-settings/positions/{position_id}/` | 获取岗位详情。 |
| `PUT` | `/position-settings/positions/{position_id}/` | 更新岗位。 |
| `DELETE` | `/position-settings/positions/{position_id}/` | 删除岗位（软删除）。 |
| `POST` | `/position-settings/positions/{position_id}/assign-resumes/` | 将简历分配到岗位。 |
| `DELETE` | `/position-settings/positions/{position_id}/remove-resume/{resume_id}/` | 从岗位移除简历。 |
| `POST` | `/position-settings/ai/generate/` | 根据用户输入生成岗位要求。 |
| `GET` | `/position-settings/list/` | 获取所有岗位标准。 |
| `POST` | `/position-settings/list/` | 创建新岗位。 |


## 简历筛选 {resume_screening}

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/resume-screening/screening/` | 提交简历筛选任务。 |
| `GET` | `/resume-screening/tasks/{task_id}/status/` | 获取任务状态。 |
| `GET` | `/resume-screening/tasks-history/` | 获取任务历史，支持分页。 |
| `DELETE` | `/resume-screening/tasks/{task_id}/` | 删除指定任务及其关联数据。 |
| `GET` | `/resume-screening/reports/{report_id}/download/` | 下载筛选报告。 |
| `GET` | `/resume-screening/reports/{report_id}/detail/` | 获取简历数据详情。 |
| `GET` | `/resume-screening/data/` | 获取简历数据列表，支持过滤和分页。 |
| `POST` | `/resume-screening/data/` | 创建新的简历数据记录。 |
| `POST` | `/resume-screening/groups/create/` | 创建简历组。 |
| `POST` | `/resume-screening/groups/add-resume/` | 向组中添加简历。 |
| `POST` | `/resume-screening/groups/remove-resume/` | 从组中移除简历。 |
| `POST` | `/resume-screening/groups/set-status/` | 设置组状态。 |
| `GET` | `/resume-screening/groups/{group_id}/` | 获取简历组详情。 |
| `GET` | `/resume-screening/groups/` | 获取简历组列表，支持过滤和分页。 |
| `POST` | `/resume-screening/link-resume-to-video/` | 将简历数据与视频分析关联。 |
| `POST` | `/resume-screening/unlink-resume-from-video/` | 解除简历数据与视频分析的关联。 |
| `GET` | `/resume-screening/library/` | 获取简历库列表 |
| `POST` | `/resume-screening/library/` | 上传简历到简历库（支持批量上传） |
| `GET` | `/resume-screening/library/{resume_id}/` | 获取简历详情 |
| `PUT` | `/resume-screening/library/{resume_id}/` | 更新简历信息 |
| `DELETE` | `/resume-screening/library/{resume_id}/` | 删除简历 |
| `POST` | `/resume-screening/library/batch-delete/` | 批量删除简历 |
| `POST` | `/resume-screening/library/check-hash/` | 检查哈希值列表 |
| `POST` | `/resume-screening/dev/generate-resumes/` | 生成随机简历并添加到简历库 |
| `GET` | `/resume-screening/dev/force-screening-error/` | 查询当前强制错误状态 |
| `POST` | `/resume-screening/dev/force-screening-error/` | 设置/取消强制筛选任务失败的标志 |
| `POST` | `/resume-screening/dev/reset-test-state/` | 重置所有测试状态 |


## 视频分析 {video_analysis}

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/video-analysis/` | 上传视频并开始分析。 |
| `GET` | `/video-analysis/{video_id}/status/` | 获取视频分析状态。 |
| `POST` | `/video-analysis/{video_id}/update/` | 更新视频分析结果。 |
| `GET` | `/video-analysis/list/` | 获取视频分析列表，支持过滤和分页。 |


## 最终推荐 {final_recommend}

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/final-recommend/comprehensive-analysis/{resume_id}/` | 获取候选人的分析历史。 |
| `POST` | `/final-recommend/comprehensive-analysis/{resume_id}/` | 执行单人综合分析。 |


## 面试辅助 {interview_assist}

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/interview-assist/sessions/` | 获取会话详情或列表。 |
| `POST` | `/interview-assist/sessions/` | 创建面试会话。 |
| `DELETE` | `/interview-assist/sessions/` | 删除会话。 |
| `GET` | `/interview-assist/sessions/{session_id}/` | 获取会话详情或列表。 |
| `POST` | `/interview-assist/sessions/{session_id}/` | 创建面试会话。 |
| `DELETE` | `/interview-assist/sessions/{session_id}/` | 删除会话。 |
| `POST` | `/interview-assist/sessions/{session_id}/generate-questions/` | 生成候选问题。 |
| `POST` | `/interview-assist/sessions/{session_id}/record-qa/` | 记录问答并生成候选提问。 |
| `POST` | `/interview-assist/sessions/{session_id}/generate-report/` | 生成最终报告。 |


## 其他 {other}

| 方法 | 路径 | 说明 |
|------|------|------|
| `ALL` | `/^media/(?P<path}.*)$/` | Serve static files below a given point in the d... |
| `ALL` | `/^static/(?P<path}.*)$/` | Serve static files below a given point in the d... |


---

## API 详细说明

### 岗位设置

#### `/position-settings/`

- **视图**: `RecruitmentCriteriaView`
- **描述**: 招聘标准API
- **路由名**: `criteria`
- **方法**:
  - `GET`: 获取招聘标准。
  - `POST`: 更新招聘标准。


#### `/position-settings/positions/`

- **视图**: `PositionCriteriaListView`
- **描述**: 岗位标准列表API
- **路由名**: `positions-list`
- **方法**:
  - `GET`: 获取所有岗位标准。
  - `POST`: 创建新岗位。


#### `/position-settings/positions/{position_id}/`

- **视图**: `PositionCriteriaDetailView`
- **描述**: 单个岗位API
- **路由名**: `position-detail`
- **方法**:
  - `GET`: 获取岗位详情。
  - `PUT`: 更新岗位。
  - `DELETE`: 删除岗位（软删除）。


#### `/position-settings/positions/{position_id}/assign-resumes/`

- **视图**: `PositionAssignResumesView`
- **描述**: 岗位简历分配API
- **路由名**: `assign-resumes`
- **方法**:
  - `POST`: 将简历分配到岗位。


#### `/position-settings/positions/{position_id}/remove-resume/{resume_id}/`

- **视图**: `PositionRemoveResumeView`
- **描述**: 从岗位移除简历API
- **路由名**: `remove-resume`
- **方法**:
  - `DELETE`: 从岗位移除简历。


#### `/position-settings/ai/generate/`

- **视图**: `PositionAIGenerateView`
- **描述**: AI生成岗位要求API
- **路由名**: `ai-generate`
- **方法**:
  - `POST`: 根据用户输入生成岗位要求。


#### `/position-settings/list/`

- **视图**: `PositionCriteriaListView`
- **描述**: 岗位标准列表API
- **路由名**: `list`
- **方法**:
  - `GET`: 获取所有岗位标准。
  - `POST`: 创建新岗位。


### 简历筛选

#### `/resume-screening/screening/`

- **视图**: `ResumeScreeningView`
- **描述**: 简历初筛API
- **路由名**: `screening`
- **方法**:
  - `POST`: 提交简历筛选任务。


#### `/resume-screening/tasks/{task_id}/status/`

- **视图**: `ScreeningTaskStatusView`
- **描述**: 查询筛选任务状态API
- **路由名**: `task-status`
- **方法**:
  - `GET`: 获取任务状态。


#### `/resume-screening/tasks-history/`

- **视图**: `TaskHistoryView`
- **描述**: 任务历史API
- **路由名**: `task-history`
- **方法**:
  - `GET`: 获取任务历史，支持分页。


#### `/resume-screening/tasks/{task_id}/`

- **视图**: `TaskDeleteView`
- **描述**: 删除任务API
- **路由名**: `task-delete`
- **方法**:
  - `DELETE`: 删除指定任务及其关联数据。


#### `/resume-screening/reports/{report_id}/download/`

- **视图**: `ReportDownloadView`
- **描述**: 报告下载API
- **路由名**: `report-download`
- **方法**:
  - `GET`: 下载筛选报告。


#### `/resume-screening/reports/{report_id}/detail/`

- **视图**: `ResumeDataDetailView`
- **描述**: 简历数据详情API
- **路由名**: `report-detail`
- **方法**:
  - `GET`: 获取简历数据详情。


#### `/resume-screening/data/`

- **视图**: `ResumeDataView`
- **描述**: 简历数据管理API
- **路由名**: `resume-data`
- **方法**:
  - `GET`: 获取简历数据列表，支持过滤和分页。
  - `POST`: 创建新的简历数据记录。


#### `/resume-screening/groups/create/`

- **视图**: `CreateResumeGroupView`
- **描述**: 创建简历组API
- **路由名**: `group-create`
- **方法**:
  - `POST`: 创建简历组。


#### `/resume-screening/groups/add-resume/`

- **视图**: `AddResumeToGroupView`
- **描述**: 添加简历到组API
- **路由名**: `group-add-resume`
- **方法**:
  - `POST`: 向组中添加简历。


#### `/resume-screening/groups/remove-resume/`

- **视图**: `RemoveResumeFromGroupView`
- **描述**: 从组中移除简历API
- **路由名**: `group-remove-resume`
- **方法**:
  - `POST`: 从组中移除简历。


#### `/resume-screening/groups/set-status/`

- **视图**: `SetGroupStatusView`
- **描述**: 设置简历组状态API
- **路由名**: `group-set-status`
- **方法**:
  - `POST`: 设置组状态。


#### `/resume-screening/groups/{group_id}/`

- **视图**: `ResumeGroupDetailView`
- **描述**: 简历组详情API
- **路由名**: `group-detail`
- **方法**:
  - `GET`: 获取简历组详情。


#### `/resume-screening/groups/`

- **视图**: `ResumeGroupListView`
- **描述**: 简历组列表API
- **路由名**: `group-list`
- **方法**:
  - `GET`: 获取简历组列表，支持过滤和分页。


#### `/resume-screening/link-resume-to-video/`

- **视图**: `LinkResumeVideoView`
- **描述**: 关联简历与视频API
- **路由名**: `link-video`
- **方法**:
  - `POST`: 将简历数据与视频分析关联。


#### `/resume-screening/unlink-resume-from-video/`

- **视图**: `UnlinkResumeVideoView`
- **描述**: 解除简历与视频关联API
- **路由名**: `unlink-video`
- **方法**:
  - `POST`: 解除简历数据与视频分析的关联。


#### `/resume-screening/library/`

- **视图**: `ResumeLibraryListView`
- **描述**: 简历库列表API
- **路由名**: `library-list`
- **方法**:
  - `GET`: 获取简历库列表
  - `POST`: 上传简历到简历库（支持批量上传）


#### `/resume-screening/library/{resume_id}/`

- **视图**: `ResumeLibraryDetailView`
- **描述**: 简历库详情API
- **路由名**: `library-detail`
- **方法**:
  - `GET`: 获取简历详情
  - `PUT`: 更新简历信息
  - `DELETE`: 删除简历


#### `/resume-screening/library/batch-delete/`

- **视图**: `ResumeLibraryBatchDeleteView`
- **描述**: 批量删除简历
- **路由名**: `library-batch-delete`
- **方法**:
  - `POST`: 批量删除简历


#### `/resume-screening/library/check-hash/`

- **视图**: `ResumeLibraryCheckHashView`
- **描述**: 检查简历哈希值是否已存在
- **路由名**: `library-check-hash`
- **方法**:
  - `POST`: 检查哈希值列表


#### `/resume-screening/dev/generate-resumes/`

- **视图**: `GenerateRandomResumesView`
- **描述**: 生成随机简历API
- **路由名**: `dev-generate-resumes`
- **方法**:
  - `POST`: 生成随机简历并添加到简历库


#### `/resume-screening/dev/force-screening-error/`

- **视图**: `ForceScreeningErrorView`
- **描述**: 强制简历筛选任务失败测试钩子
- **路由名**: `dev-force-error`
- **方法**:
  - `GET`: 查询当前强制错误状态
  - `POST`: 设置/取消强制筛选任务失败的标志


#### `/resume-screening/dev/reset-test-state/`

- **视图**: `ResetScreeningTestStateView`
- **描述**: 重置简历筛选测试状态
- **路由名**: `dev-reset-state`
- **方法**:
  - `POST`: 重置所有测试状态


### 视频分析

#### `/video-analysis/`

- **视图**: `VideoAnalysisView`
- **描述**: 视频分析API
- **路由名**: `upload`
- **方法**:
  - `POST`: 上传视频并开始分析。


#### `/video-analysis/{video_id}/status/`

- **视图**: `VideoAnalysisStatusView`
- **描述**: 视频分析状态API
- **路由名**: `status`
- **方法**:
  - `GET`: 获取视频分析状态。


#### `/video-analysis/{video_id}/update/`

- **视图**: `VideoAnalysisUpdateView`
- **描述**: 视频分析结果更新API
- **路由名**: `update`
- **方法**:
  - `POST`: 更新视频分析结果。


#### `/video-analysis/list/`

- **视图**: `VideoAnalysisListView`
- **描述**: 视频分析列表API
- **路由名**: `list`
- **方法**:
  - `GET`: 获取视频分析列表，支持过滤和分页。


### 最终推荐

#### `/final-recommend/comprehensive-analysis/{resume_id}/`

- **视图**: `CandidateComprehensiveAnalysisView`
- **描述**: 单人综合分析API
- **路由名**: `comprehensive-analysis`
- **方法**:
  - `GET`: 获取候选人的分析历史。
  - `POST`: 执行单人综合分析。


### 面试辅助

#### `/interview-assist/sessions/`

- **视图**: `SessionView`
- **描述**: 面试会话API
- **路由名**: `session-create`
- **方法**:
  - `GET`: 获取会话详情或列表。
  - `POST`: 创建面试会话。
  - `DELETE`: 删除会话。


#### `/interview-assist/sessions/{session_id}/`

- **视图**: `SessionView`
- **描述**: 面试会话API
- **路由名**: `session-detail`
- **方法**:
  - `GET`: 获取会话详情或列表。
  - `POST`: 创建面试会话。
  - `DELETE`: 删除会话。


#### `/interview-assist/sessions/{session_id}/generate-questions/`

- **视图**: `GenerateQuestionsView`
- **描述**: 生成问题API
- **路由名**: `generate-questions`
- **方法**:
  - `POST`: 生成候选问题。


#### `/interview-assist/sessions/{session_id}/record-qa/`

- **视图**: `RecordQAView`
- **描述**: 记录问答API
- **路由名**: `record-qa`
- **方法**:
  - `POST`: 记录问答并生成候选提问。


#### `/interview-assist/sessions/{session_id}/generate-report/`

- **视图**: `GenerateReportView`
- **描述**: 生成报告API
- **路由名**: `generate-report`
- **方法**:
  - `POST`: 生成最终报告。


### 其他

#### `/^media/(?P<path}.*)$/`

- **视图**: `serve`
- **描述**: Serve static files below a given point in the directory structure.
- **方法**:
  - `ALL`: Serve static files below a given point in the directory structure.


#### `/^static/(?P<path}.*)$/`

- **视图**: `serve`
- **描述**: Serve static files below a given point in the directory structure.
- **方法**:
  - `ALL`: Serve static files below a given point in the directory structure.

