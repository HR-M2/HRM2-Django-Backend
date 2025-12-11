# HR招聘系统 API

> **版本**: 1.0.0
> **生成时间**: 2025-12-11 14:22:20

智能招聘管理系统后端API文档

## 功能模块
- **岗位设置** - 岗位标准管理、简历分配
- **简历筛选** - 简历上传与AI初筛
- **视频分析** - 面试视频分析（预留）
- **面试辅助** - AI面试问答助手
- **最终推荐** - 候选人综合评估

---

## 概览

共 **54** 个API端点，分布在 **5** 个模块中。

## 目录

- [岗位设置](#position-settings) (12个接口)
- [简历筛选](#resume-screening) (27个接口)
- [视频分析](#video-analysis) (4个接口)
- [最终推荐](#final-recommend) (2个接口)
- [面试辅助](#interview-assist) (9个接口)

---

## 快速参考

### 岗位设置

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /position-settings/ | position_settings_retrieve |
| 🟡 POST | /position-settings/ | position_settings_create |
| 🟡 POST | /position-settings/ai/generate/ | position_settings_ai_generate_create |
| 🟢 GET | /position-settings/list/ | position_settings_list_retrieve |
| 🟡 POST | /position-settings/list/ | position_settings_list_create |
| 🟢 GET | /position-settings/positions/ | position_settings_positions_retrieve |
| 🟡 POST | /position-settings/positions/ | position_settings_positions_create |
| 🟢 GET | /position-settings/positions/`{position_id}`/ | position_settings_positions_retrieve_2 |
| 🟠 PUT | /position-settings/positions/`{position_id}`/ | position_settings_positions_update |
| 🔴 DELETE | /position-settings/positions/`{position_id}`/ | position_settings_positions_destroy |
| 🟡 POST | /position-settings/positions/`{position_id}`/assign-resumes/ | position_settings_positions_assign_resumes_create |
| 🔴 DELETE | /position-settings/positions/`{position_id}`/remove-resume/`{resume_id}`/ | position_settings_positions_remove_resume_destroy |

### 简历筛选

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /resume-screening/data/ | resume_screening_data_retrieve |
| 🟡 POST | /resume-screening/data/ | resume_screening_data_create |
| 🟢 GET | /resume-screening/dev/force-screening-error/ | resume_screening_dev_force_screening_error_retrieve |
| 🟡 POST | /resume-screening/dev/force-screening-error/ | resume_screening_dev_force_screening_error_create |
| 🟡 POST | /resume-screening/dev/generate-resumes/ | resume_screening_dev_generate_resumes_create |
| 🟡 POST | /resume-screening/dev/reset-test-state/ | resume_screening_dev_reset_test_state_create |
| 🟢 GET | /resume-screening/groups/ | resume_screening_groups_retrieve |
| 🟡 POST | /resume-screening/groups/add-resume/ | resume_screening_groups_add_resume_create |
| 🟡 POST | /resume-screening/groups/create/ | resume_screening_groups_create_create |
| 🟡 POST | /resume-screening/groups/remove-resume/ | resume_screening_groups_remove_resume_create |
| 🟡 POST | /resume-screening/groups/set-status/ | resume_screening_groups_set_status_create |
| 🟢 GET | /resume-screening/groups/`{group_id}`/ | resume_screening_groups_retrieve_2 |
| 🟢 GET | /resume-screening/library/ | resume_screening_library_retrieve |
| 🟡 POST | /resume-screening/library/ | resume_screening_library_create |
| 🟡 POST | /resume-screening/library/batch-delete/ | resume_screening_library_batch_delete_create |
| 🟡 POST | /resume-screening/library/check-hash/ | resume_screening_library_check_hash_create |
| 🟢 GET | /resume-screening/library/`{resume_id}`/ | resume_screening_library_retrieve_2 |
| 🟠 PUT | /resume-screening/library/`{resume_id}`/ | resume_screening_library_update |
| 🔴 DELETE | /resume-screening/library/`{resume_id}`/ | resume_screening_library_destroy |
| 🟡 POST | /resume-screening/link-resume-to-video/ | resume_screening_link_resume_to_video_create |
| 🟢 GET | /resume-screening/reports/`{report_id}`/detail/ | resume_screening_reports_detail_retrieve |
| 🟢 GET | /resume-screening/reports/`{report_id}`/download/ | resume_screening_reports_download_retrieve |
| 🟡 POST | /resume-screening/screening/ | resume_screening_screening_create |
| 🟢 GET | /resume-screening/tasks-history/ | resume_screening_tasks_history_retrieve |
| 🔴 DELETE | /resume-screening/tasks/`{task_id}`/ | resume_screening_tasks_destroy |
| 🟢 GET | /resume-screening/tasks/`{task_id}`/status/ | resume_screening_tasks_status_retrieve |
| 🟡 POST | /resume-screening/unlink-resume-from-video/ | resume_screening_unlink_resume_from_video_create |

### 视频分析

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟡 POST | /video-analysis/ | video_analysis_create |
| 🟢 GET | /video-analysis/list/ | video_analysis_list_retrieve |
| 🟢 GET | /video-analysis/`{video_id}`/status/ | video_analysis_status_retrieve |
| 🟡 POST | /video-analysis/`{video_id}`/update/ | video_analysis_update_create |

### 最终推荐

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /final-recommend/comprehensive-analysis/`{resume_id}`/ | final_recommend_comprehensive_analysis_retrieve |
| 🟡 POST | /final-recommend/comprehensive-analysis/`{resume_id}`/ | final_recommend_comprehensive_analysis_create |

### 面试辅助

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /interview-assist/sessions/ | interview_assist_sessions_retrieve |
| 🟡 POST | /interview-assist/sessions/ | interview_assist_sessions_create |
| 🔴 DELETE | /interview-assist/sessions/ | interview_assist_sessions_destroy |
| 🟢 GET | /interview-assist/sessions/`{session_id}`/ | interview_assist_sessions_retrieve_2 |
| 🟡 POST | /interview-assist/sessions/`{session_id}`/ | interview_assist_sessions_create_2 |
| 🔴 DELETE | /interview-assist/sessions/`{session_id}`/ | interview_assist_sessions_destroy_2 |
| 🟡 POST | /interview-assist/sessions/`{session_id}`/generate-questions/ | interview_assist_sessions_generate_questions_create |
| 🟡 POST | /interview-assist/sessions/`{session_id}`/generate-report/ | interview_assist_sessions_generate_report_create |
| 🟡 POST | /interview-assist/sessions/`{session_id}`/record-qa/ | interview_assist_sessions_record_qa_create |

---

## 接口详情

### 岗位设置

#### 🟢 GET `/position-settings/`

招聘标准API
GET: 获取当前招聘标准
POST: 更新招聘标准

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/position-settings/`

招聘标准API
GET: 获取当前招聘标准
POST: 更新招聘标准

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/position-settings/ai/generate/`

AI生成岗位要求API
POST: 根据描述和文档生成岗位要求

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/position-settings/list/`

岗位标准列表API
GET: 获取所有岗位标准列表
POST: 创建新岗位

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/position-settings/list/`

岗位标准列表API
GET: 获取所有岗位标准列表
POST: 创建新岗位

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/position-settings/positions/`

岗位标准列表API
GET: 获取所有岗位标准列表
POST: 创建新岗位

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/position-settings/positions/`

岗位标准列表API
GET: 获取所有岗位标准列表
POST: 创建新岗位

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/position-settings/positions/{position_id}/`

单个岗位API
GET: 获取岗位详情
PUT: 更新岗位
DELETE: 删除岗位（软删除）

**参数**:

  - `position_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟠 PUT `/position-settings/positions/{position_id}/`

单个岗位API
GET: 获取岗位详情
PUT: 更新岗位
DELETE: 删除岗位（软删除）

**参数**:

  - `position_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/position-settings/positions/{position_id}/`

单个岗位API
GET: 获取岗位详情
PUT: 更新岗位
DELETE: 删除岗位（软删除）

**参数**:

  - `position_id` (string, path, 必填): 

**响应**:

  - `204`: No response body

---

#### 🟡 POST `/position-settings/positions/{position_id}/assign-resumes/`

岗位简历分配API
POST: 将简历分配到岗位

**参数**:

  - `position_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/position-settings/positions/{position_id}/remove-resume/{resume_id}/`

从岗位移除简历API
DELETE: 从岗位移除指定简历

**参数**:

  - `position_id` (string, path, 必填): 
  - `resume_id` (string, path, 必填): 

**响应**:

  - `204`: No response body

---

### 简历筛选

#### 🟢 GET `/resume-screening/data/`

简历数据管理API
GET: 获取简历数据列表
POST: 创建新的简历数据

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/data/`

简历数据管理API
GET: 获取简历数据列表
POST: 创建新的简历数据

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/resume-screening/dev/force-screening-error/`

强制简历筛选任务失败测试钩子
POST: 通过环境变量控制是否强制筛选任务失败

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/dev/force-screening-error/`

强制简历筛选任务失败测试钩子
POST: 通过环境变量控制是否强制筛选任务失败

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/dev/generate-resumes/`

生成随机简历API
POST: 根据岗位要求生成随机简历并添加到简历库

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/dev/reset-test-state/`

重置简历筛选测试状态
POST: 清除所有测试相关的缓存和状态

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/resume-screening/groups/`

简历组列表API
GET: 获取简历组列表

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/groups/add-resume/`

添加简历到组API
POST: 向简历组添加简历

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/groups/create/`

创建简历组API
POST: 创建新的简历组

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/groups/remove-resume/`

从组中移除简历API
POST: 从简历组移除简历

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/groups/set-status/`

设置简历组状态API
POST: 更新简历组状态

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/resume-screening/groups/{group_id}/`

简历组详情API
GET: 获取简历组详情

**参数**:

  - `group_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/resume-screening/library/`

简历库列表API
GET: 获取简历库列表（支持分页和筛选）
POST: 上传简历到简历库

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/library/`

简历库列表API
GET: 获取简历库列表（支持分页和筛选）
POST: 上传简历到简历库

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/library/batch-delete/`

批量删除简历

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/library/check-hash/`

检查简历哈希值是否已存在

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/resume-screening/library/{resume_id}/`

简历库详情API
GET: 获取简历详情
PUT: 更新简历信息
DELETE: 删除简历

**参数**:

  - `resume_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟠 PUT `/resume-screening/library/{resume_id}/`

简历库详情API
GET: 获取简历详情
PUT: 更新简历信息
DELETE: 删除简历

**参数**:

  - `resume_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/resume-screening/library/{resume_id}/`

简历库详情API
GET: 获取简历详情
PUT: 更新简历信息
DELETE: 删除简历

**参数**:

  - `resume_id` (string, path, 必填): 

**响应**:

  - `204`: No response body

---

#### 🟡 POST `/resume-screening/link-resume-to-video/`

关联简历与视频API
POST: 建立简历与视频分析的关联

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/resume-screening/reports/{report_id}/detail/`

简历数据详情API
GET: 获取简历数据详情

**参数**:

  - `report_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/resume-screening/reports/{report_id}/download/`

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

#### 🟡 POST `/resume-screening/screening/`

简历初筛API
POST: 提交简历筛选任务

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/resume-screening/tasks-history/`

任务历史API
GET: 获取历史任务列表
DELETE: 删除指定任务

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/resume-screening/tasks/{task_id}/`

删除任务API
DELETE: 删除指定任务

**参数**:

  - `task_id` (string, path, 必填): 

**响应**:

  - `204`: No response body

---

#### 🟢 GET `/resume-screening/tasks/{task_id}/status/`

查询筛选任务状态API
GET: 获取任务状态和结果

**参数**:

  - `task_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/resume-screening/unlink-resume-from-video/`

解除简历与视频关联API
POST: 解除简历与视频分析的关联

**响应**:

  - `200`: No response body

---

### 视频分析

#### 🟡 POST `/video-analysis/`

视频分析API
POST: 上传视频并开始分析

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/video-analysis/list/`

视频分析列表API
GET: 获取视频分析列表

**响应**:

  - `200`: No response body

---

#### 🟢 GET `/video-analysis/{video_id}/status/`

视频分析状态API
GET: 获取视频分析状态和结果

**参数**:

  - `video_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/video-analysis/{video_id}/update/`

视频分析结果更新API
POST: 更新视频分析结果

**参数**:

  - `video_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

### 最终推荐

#### 🟢 GET `/final-recommend/comprehensive-analysis/{resume_id}/`

单人综合分析API
POST: 对单个候选人进行综合分析
GET: 获取候选人的分析历史

**参数**:

  - `resume_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/final-recommend/comprehensive-analysis/{resume_id}/`

单人综合分析API
POST: 对单个候选人进行综合分析
GET: 获取候选人的分析历史

**参数**:

  - `resume_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

### 面试辅助

#### 🟢 GET `/interview-assist/sessions/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/interview-assist/sessions/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/interview-assist/sessions/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**响应**:

  - `204`: No response body

---

#### 🟢 GET `/interview-assist/sessions/{session_id}/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/interview-assist/sessions/{session_id}/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🔴 DELETE `/interview-assist/sessions/{session_id}/`

面试会话API
POST: 创建会话
GET: 获取会话详情
DELETE: 结束会话

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `204`: No response body

---

#### 🟡 POST `/interview-assist/sessions/{session_id}/generate-questions/`

生成问题API
POST: 生成候选问题（临时生成，不保存到数据库）

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/interview-assist/sessions/{session_id}/generate-report/`

生成报告API
POST: 生成最终报告

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---

#### 🟡 POST `/interview-assist/sessions/{session_id}/record-qa/`

记录问答API
POST: 记录问答并获取评估

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`: No response body

---
