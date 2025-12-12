# HR招聘系统 API

> **版本**: 1.0.0
> **生成时间**: 2025-12-12 11:32:29

智能招聘管理系统后端API文档

## 功能模块
- **岗位设置** - 岗位标准管理、简历分配
- **简历筛选** - 简历上传与AI初筛
- **视频分析** - 面试视频分析（预留）
- **面试辅助** - AI面试问答助手
- **最终推荐** - 候选人综合评估

---

## 概览

共 **50** 个API端点，分布在 **6** 个模块中。

## 目录

- [岗位设置](#positions) (8个接口)
- [简历库](#library) (7个接口)
- [简历筛选](#screening) (20个接口)
- [视频分析](#videos) (4个接口)
- [最终推荐](#recommend) (2个接口)
- [面试辅助](#interviews) (9个接口)

---

## 快速参考

### 岗位设置

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /api/positions/ | positions_retrieve |
| 🟡 POST | /api/positions/ | positions_create |
| 🟡 POST | /api/positions/ai/generate/ | positions_ai_generate_create |
| 🟢 GET | /api/positions/`{position_id}`/ | positions_retrieve_2 |
| 🟠 PUT | /api/positions/`{position_id}`/ | positions_update |
| 🔴 DELETE | /api/positions/`{position_id}`/ | positions_destroy |
| 🟡 POST | /api/positions/`{position_id}`/resumes/ | positions_resumes_create |
| 🔴 DELETE | /api/positions/`{position_id}`/resumes/`{resume_id}`/ | positions_resumes_destroy |

### 简历库

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /api/library/ | library_retrieve |
| 🟡 POST | /api/library/ | library_create |
| 🟡 POST | /api/library/batch-delete/ | library_batch_delete_create |
| 🟡 POST | /api/library/check-hash/ | library_check_hash_create |
| 🟢 GET | /api/library/`{id}`/ | library_retrieve_2 |
| 🟠 PUT | /api/library/`{id}`/ | library_update |
| 🔴 DELETE | /api/library/`{id}`/ | library_destroy |

### 简历筛选

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟡 POST | /api/screening/ | screening_create |
| 🟢 GET | /api/screening/data/ | screening_data_retrieve |
| 🟡 POST | /api/screening/data/ | screening_data_create |
| 🟢 GET | /api/screening/dev/force-error/ | screening_dev_force_error_retrieve |
| 🟡 POST | /api/screening/dev/force-error/ | screening_dev_force_error_create |
| 🟡 POST | /api/screening/dev/generate-resumes/ | screening_dev_generate_resumes_create |
| 🟡 POST | /api/screening/dev/reset-state/ | screening_dev_reset_state_create |
| 🟢 GET | /api/screening/groups/ | screening_groups_retrieve |
| 🟡 POST | /api/screening/groups/add-resume/ | screening_groups_add_resume_create |
| 🟡 POST | /api/screening/groups/create/ | screening_groups_create_create |
| 🟡 POST | /api/screening/groups/remove-resume/ | screening_groups_remove_resume_create |
| 🟡 POST | /api/screening/groups/set-status/ | screening_groups_set_status_create |
| 🟢 GET | /api/screening/groups/`{group_id}`/ | screening_groups_retrieve_2 |
| 🟢 GET | /api/screening/reports/`{report_id}`/ | screening_reports_retrieve |
| 🟢 GET | /api/screening/reports/`{report_id}`/download/ | screening_reports_download_retrieve |
| 🟢 GET | /api/screening/tasks/ | screening_tasks_retrieve |
| 🔴 DELETE | /api/screening/tasks/`{task_id}`/ | screening_tasks_destroy |
| 🟢 GET | /api/screening/tasks/`{task_id}`/status/ | screening_tasks_status_retrieve |
| 🟡 POST | /api/screening/videos/link/ | screening_videos_link_create |
| 🟡 POST | /api/screening/videos/unlink/ | screening_videos_unlink_create |

### 视频分析

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /api/videos/ | videos_retrieve |
| 🟡 POST | /api/videos/upload/ | videos_upload_create |
| 🟡 POST | /api/videos/`{video_id}`/ | videos_create |
| 🟢 GET | /api/videos/`{video_id}`/status/ | videos_status_retrieve |

### 最终推荐

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /api/recommend/analysis/`{resume_id}`/ | recommend_analysis_retrieve |
| 🟡 POST | /api/recommend/analysis/`{resume_id}`/ | recommend_analysis_create |

### 面试辅助

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /api/interviews/sessions/ | interviews_sessions_retrieve |
| 🟡 POST | /api/interviews/sessions/ | interviews_sessions_create |
| 🔴 DELETE | /api/interviews/sessions/ | interviews_sessions_destroy |
| 🟢 GET | /api/interviews/sessions/`{session_id}`/ | interviews_sessions_retrieve_2 |
| 🟡 POST | /api/interviews/sessions/`{session_id}`/ | interviews_sessions_create_2 |
| 🔴 DELETE | /api/interviews/sessions/`{session_id}`/ | interviews_sessions_destroy_2 |
| 🟡 POST | /api/interviews/sessions/`{session_id}`/qa/ | interviews_sessions_qa_create |
| 🟡 POST | /api/interviews/sessions/`{session_id}`/questions/ | interviews_sessions_questions_create |
| 🟡 POST | /api/interviews/sessions/`{session_id}`/report/ | interviews_sessions_report_create |

---

## 接口详情

### 岗位设置

#### 🟢 GET `/api/positions/`

岗位标准列表API
GET: 获取所有岗位标准列表
POST: 创建新岗位

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/positions/`

岗位标准列表API
GET: 获取所有岗位标准列表
POST: 创建新岗位

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/positions/ai/generate/`

AI生成岗位要求API
POST: 根据描述和文档生成岗位要求

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/api/positions/{position_id}/`

单个岗位API
GET: 获取岗位详情
PUT: 更新岗位
DELETE: 删除岗位（软删除）

**参数**:

  - `position_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟠 PUT `/api/positions/{position_id}/`

单个岗位API
GET: 获取岗位详情
PUT: 更新岗位
DELETE: 删除岗位（软删除）

**参数**:

  - `position_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/api/positions/{position_id}/`

单个岗位API
GET: 获取岗位详情
PUT: 更新岗位
DELETE: 删除岗位（软删除）

**参数**:

  - `position_id` (string, path, 必填): 

**响应**:

  - `204`: No response body

---

#### 🟡 POST `/api/positions/{position_id}/resumes/`

岗位简历分配API
POST: 将简历分配到岗位

**参数**:

  - `position_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/api/positions/{position_id}/resumes/{resume_id}/`

从岗位移除简历API
DELETE: 从岗位移除指定简历

**参数**:

  - `position_id` (string, path, 必填): 
  - `resume_id` (string, path, 必填): 

**响应**:

  - `204`: No response body

---

### 简历库

#### 🟢 GET `/api/library/`

简历库列表API。

GET: 获取简历库列表（支持分页和筛选）
POST: 上传简历到简历库

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/library/`

简历库列表API。

GET: 获取简历库列表（支持分页和筛选）
POST: 上传简历到简历库

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/library/batch-delete/`

批量删除简历API。

POST: 批量删除简历

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/library/check-hash/`

检查简历哈希值是否已存在API。

POST: 检查哈希值列表

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/api/library/{id}/`

简历库详情API。

GET: 获取简历详情
PUT: 更新简历信息
DELETE: 删除简历

**参数**:

  - `id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟠 PUT `/api/library/{id}/`

简历库详情API。

GET: 获取简历详情
PUT: 更新简历信息
DELETE: 删除简历

**参数**:

  - `id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/api/library/{id}/`

简历库详情API。

GET: 获取简历详情
PUT: 更新简历信息
DELETE: 删除简历

**参数**:

  - `id` (string, path, 必填): 

**响应**:

  - `204`: No response body

---

### 简历筛选

#### 🟡 POST `/api/screening/`

简历初筛API
POST: 提交简历筛选任务

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/api/screening/data/`

简历数据管理API
GET: 获取简历数据列表
POST: 创建新的简历数据

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/screening/data/`

简历数据管理API
GET: 获取简历数据列表
POST: 创建新的简历数据

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/api/screening/dev/force-error/`

强制简历筛选任务失败测试钩子
POST: 通过环境变量控制是否强制筛选任务失败

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/screening/dev/force-error/`

强制简历筛选任务失败测试钩子
POST: 通过环境变量控制是否强制筛选任务失败

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/screening/dev/generate-resumes/`

生成随机简历API
POST: 根据岗位要求生成随机简历并添加到简历库

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/screening/dev/reset-state/`

重置简历筛选测试状态
POST: 清除所有测试相关的缓存和状态

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/api/screening/groups/`

简历组列表API
GET: 获取简历组列表

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/screening/groups/add-resume/`

添加简历到组API
POST: 向简历组添加简历

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/screening/groups/create/`

创建简历组API
POST: 创建新的简历组

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/screening/groups/remove-resume/`

从组中移除简历API
POST: 从简历组移除简历

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/screening/groups/set-status/`

设置简历组状态API
POST: 更新简历组状态

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/api/screening/groups/{group_id}/`

简历组详情API
GET: 获取简历组详情

**参数**:

  - `group_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/api/screening/reports/{report_id}/`

简历数据详情API
GET: 获取简历数据详情

**参数**:

  - `report_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/api/screening/reports/{report_id}/download/`

报告下载API
GET: 下载筛选报告

支持两种方式：
1. 如果有 md_file，直接返回文件
2. 如果没有文件，从数据库的 ResumeData 动态生成 Markdown 报告

**参数**:

  - `report_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/api/screening/tasks/`

任务历史API
GET: 获取历史任务列表
DELETE: 删除指定任务

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/api/screening/tasks/{task_id}/`

删除任务API
DELETE: 删除指定任务

**参数**:

  - `task_id` (string, path, 必填): 

**响应**:

  - `204`: No response body

---

#### 🟢 GET `/api/screening/tasks/{task_id}/status/`

查询筛选任务状态API
GET: 获取任务状态和结果

**参数**:

  - `task_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/screening/videos/link/`

关联简历与视频API
POST: 建立简历与视频分析的关联

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/screening/videos/unlink/`

解除简历与视频关联API
POST: 解除简历与视频分析的关联

**响应**:

  - `200`: No response body

---

### 视频分析

#### 🟢 GET `/api/videos/`

视频分析列表API
GET: 获取视频分析列表

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/videos/upload/`

视频分析API
POST: 上传视频并开始分析

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/videos/{video_id}/`

视频分析结果更新API
POST: 更新视频分析结果

**参数**:

  - `video_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/api/videos/{video_id}/status/`

视频分析状态API
GET: 获取视频分析状态和结果

**参数**:

  - `video_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

### 最终推荐

#### 🟢 GET `/api/recommend/analysis/{resume_id}/`

单人综合分析API
POST: 对单个候选人进行综合分析
GET: 获取候选人的分析历史

**参数**:

  - `resume_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/recommend/analysis/{resume_id}/`

单人综合分析API
POST: 对单个候选人进行综合分析
GET: 获取候选人的分析历史

**参数**:

  - `resume_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

### 面试辅助

#### 🟢 GET `/api/interviews/sessions/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/interviews/sessions/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/api/interviews/sessions/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**响应**:

  - `204`: No response body

---

#### 🟢 GET `/api/interviews/sessions/{session_id}/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/interviews/sessions/{session_id}/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/api/interviews/sessions/{session_id}/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `204`: No response body

---

#### 🟡 POST `/api/interviews/sessions/{session_id}/qa/`

记录问答API
POST: 记录问答并获取评估

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/interviews/sessions/{session_id}/questions/`

生成问题API
POST: 生成候选问题（临时生成，不保存到数据库）

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/api/interviews/sessions/{session_id}/report/`

生成报告API
POST: 生成最终报告

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---
