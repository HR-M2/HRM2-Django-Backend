# HR招聘系统 API

> **版本**: 1.0.0
> **生成时间**: 2025-12-13 16:43:15

智能招聘管理系统后端API文档

## 功能模块
- **岗位设置** - 岗位标准管理、简历分配
- **简历筛选** - 简历上传与AI初筛
- **视频分析** - 面试视频分析（预留）
- **面试辅助** - AI面试问答助手
- **最终推荐** - 候选人综合评估

---

## 概览

共 **40** 个API端点，分布在 **6** 个模块中。

## 目录

- [岗位设置](#positions) (8个接口)
- [简历库](#library) (7个接口)
- [简历筛选](#screening) (11个接口)
- [视频分析](#videos) (4个接口)
- [最终推荐](#recommend) (3个接口)
- [面试辅助](#interviews) (7个接口)

---

## 快速参考

### 岗位设置

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /api/positions/ | 获取岗位列表 |
| 🟡 POST | /api/positions/ | 创建新岗位 |
| 🟡 POST | /api/positions/ai/generate/ | AI生成岗位要求 |
| 🟢 GET | /api/positions/`{position_id}`/ | 获取岗位详情 |
| 🟠 PUT | /api/positions/`{position_id}`/ | 更新岗位 |
| 🔴 DELETE | /api/positions/`{position_id}`/ | 删除岗位 |
| 🟡 POST | /api/positions/`{position_id}`/resumes/ | 分配简历到岗位 |
| 🔴 DELETE | /api/positions/`{position_id}`/resumes/`{resume_id}`/ | 从岗位移除简历 |

### 简历库

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /api/library/ | 获取简历库列表 |
| 🟡 POST | /api/library/ | 上传简历到简历库 |
| 🟡 POST | /api/library/batch-delete/ | 批量删除简历 |
| 🟡 POST | /api/library/check-hash/ | 检查哈希值是否已存在 |
| 🟢 GET | /api/library/`{id}`/ | 获取简历详情 |
| 🟠 PUT | /api/library/`{id}`/ | 更新简历信息 |
| 🔴 DELETE | /api/library/`{id}`/ | 删除简历 |

### 简历筛选

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟡 POST | /api/screening/ | 提交简历筛选任务 |
| 🟢 GET | /api/screening/data/ | 获取简历数据列表 |
| 🟡 POST | /api/screening/data/ | 创建简历数据 |
| 🟡 POST | /api/screening/dev/generate-resumes/ | 生成随机简历 |
| 🟢 GET | /api/screening/reports/`{report_id}`/ | 获取简历数据详情 |
| 🟢 GET | /api/screening/reports/`{report_id}`/download/ | 下载筛选报告 |
| 🟢 GET | /api/screening/tasks/ | 获取任务历史列表 |
| 🔴 DELETE | /api/screening/tasks/`{task_id}`/ | 删除筛选任务 |
| 🟢 GET | /api/screening/tasks/`{task_id}`/status/ | 获取筛选任务状态 |
| 🟡 POST | /api/screening/videos/link/ | 关联简历与视频 |
| 🟡 POST | /api/screening/videos/unlink/ | 解除简历与视频关联 |

### 视频分析

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /api/videos/ | 获取视频分析列表 |
| 🟡 POST | /api/videos/upload/ | 上传视频并开始分析 |
| 🟡 POST | /api/videos/`{video_id}`/ | 更新视频分析结果 |
| 🟢 GET | /api/videos/`{video_id}`/status/ | 获取视频分析状态 |

### 最终推荐

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /api/recommend/analysis/`{resume_id}`/ | 获取综合分析历史 |
| 🟡 POST | /api/recommend/analysis/`{resume_id}`/ | 执行综合分析 |
| 🟢 GET | /api/recommend/stats/ | 获取推荐统计 |

### 面试辅助

| 方法 | 路径 | 说明 |
|:-----|:-----|:-----|
| 🟢 GET | /api/interviews/sessions/ | 获取面试会话列表 |
| 🟡 POST | /api/interviews/sessions/ | 创建面试会话 |
| 🟢 GET | /api/interviews/sessions/`{session_id}`/ | 获取会话详情 |
| 🔴 DELETE | /api/interviews/sessions/`{session_id}`/ | 删除会话 |
| 🟡 POST | /api/interviews/sessions/`{session_id}`/qa/ | 记录问答并生成候选提问 |
| 🟡 POST | /api/interviews/sessions/`{session_id}`/questions/ | 生成候选问题 |
| 🟡 POST | /api/interviews/sessions/`{session_id}`/report/ | 生成面试报告 |

---

## 接口详情

### 岗位设置

#### 🟢 GET `/api/positions/`

**获取岗位列表**

获取所有激活的岗位标准列表

**参数**:

  - `include_resumes` (boolean, query, 可选): 是否包含关联简历

**响应**:

  - `200`:  → `ApiPositionListResp`

---

#### 🟡 POST `/api/positions/`

**创建新岗位**

创建新的岗位标准

**请求体**: `PositionCreateRequestRequest`

**响应**:

  - `201`:  → `ApiPositionCreateResp`

---

#### 🟡 POST `/api/positions/ai/generate/`

**AI生成岗位要求**

根据描述和参考文档，使用AI生成岗位要求

**请求体**: `AIGenerateRequestRequest`

**响应**:

  - `200`:  → `ApiAIGenerateResp`

---

#### 🟢 GET `/api/positions/{position_id}/`

**获取岗位详情**

获取指定岗位的详细信息，包含关联简历

**参数**:

  - `include_resumes` (boolean, query, 可选): 是否包含关联简历
  - `position_id` (string, path, 必填): 

**响应**:

  - `200`:  → `ApiPositionDetailResp`

---

#### 🟠 PUT `/api/positions/{position_id}/`

**更新岗位**

更新指定岗位的信息

**参数**:

  - `position_id` (string, path, 必填): 

**请求体**: `PositionCreateRequestRequest`

**响应**:

  - `200`:  → `ApiPositionUpdateResp`

---

#### 🔴 DELETE `/api/positions/{position_id}/`

**删除岗位**

软删除指定岗位

**参数**:

  - `position_id` (string, path, 必填): 

**响应**:

  - `200`:  → `PositionDeleteResponse`

---

#### 🟡 POST `/api/positions/{position_id}/resumes/`

**分配简历到岗位**

将一个或多个简历分配到指定岗位

**参数**:

  - `position_id` (string, path, 必填): 

**请求体**: `AssignResumesRequestRequest`

**响应**:

  - `200`:  → `ApiAssignResumesResp`

---

#### 🔴 DELETE `/api/positions/{position_id}/resumes/{resume_id}/`

**从岗位移除简历**

从指定岗位移除指定简历

**参数**:

  - `position_id` (string, path, 必填): 
  - `resume_id` (string, path, 必填): 

**响应**:

  - `200`:  → `ApiRemoveResumeResp`

---

### 简历库

#### 🟢 GET `/api/library/`

**获取简历库列表**

获取简历库列表，支持分页和筛选

**参数**:

  - `is_assigned` (boolean, query, 可选): 是否已分配
  - `is_screened` (boolean, query, 可选): 是否已筛选
  - `keyword` (string, query, 可选): 关键词搜索
  - `page` (integer, query, 可选): 页码
  - `page_size` (integer, query, 可选): 每页数量

**响应**:

  - `200`:  → `ApiLibraryPaginatedResp`

---

#### 🟡 POST `/api/library/`

**上传简历到简历库**

批量上传简历到简历库，单次最多50份

**请求体**: `LibraryUploadRequestRequest`

**响应**:

  - `200`:  → `ApiLibraryUploadResp`

---

#### 🟡 POST `/api/library/batch-delete/`

**批量删除简历**

根据ID列表批量删除简历

**请求体**: `BatchDeleteRequestRequest`

**响应**:

  - `200`:  → `ApiLibraryBatchDeleteResp`

---

#### 🟡 POST `/api/library/check-hash/`

**检查哈希值是否已存在**

批量检查简历哈希值是否已存在于简历库

**请求体**: `HashCheckRequestRequest`

**响应**:

  - `200`:  → `ApiLibraryHashCheckResp`

---

#### 🟢 GET `/api/library/{id}/`

**获取简历详情**

获取指定简历的详细信息

**参数**:

  - `id` (string, path, 必填): 

**响应**:

  - `200`:  → `ApiLibraryDetailResp`

---

#### 🟠 PUT `/api/library/{id}/`

**更新简历信息**

更新指定简历的信息

**参数**:

  - `id` (string, path, 必填): 

**请求体**: `LibraryUpdateRequestRequest`

**响应**:

  - `200`:  → `ApiLibraryUpdateResp`

---

#### 🔴 DELETE `/api/library/{id}/`

**删除简历**

删除指定简历

**参数**:

  - `id` (string, path, 必填): 

**响应**:

  - `200`:  → `LibraryDeleteResponse`

---

### 简历筛选

#### 🟡 POST `/api/screening/`

**提交简历筛选任务**

提交简历筛选任务，后台异步处理

**响应**:

  - `202`:  → `ApiScreeningSubmitResp`

---

#### 🟢 GET `/api/screening/data/`

**获取简历数据列表**

获取简历数据列表，支持过滤和分页

**参数**:

  - `candidate_name` (string, query, 可选): 候选人姓名过滤
  - `page` (integer, query, 可选): 页码
  - `page_size` (integer, query, 可选): 每页数量
  - `position_title` (string, query, 可选): 岗位名称过滤

**响应**:

  - `200`:  → `ApiResumeDataListResp`

---

#### 🟡 POST `/api/screening/data/`

**创建简历数据**

创建新的简历数据记录

**请求体**: `ResumeDataCreateRequestRequest`

**响应**:

  - `201`:  → `ApiResumeDataCreateResp`

---

#### 🟡 POST `/api/screening/dev/generate-resumes/`

**生成随机简历**

根据岗位要求使用AI生成随机简历并添加到简历库（开发测试用）

**请求体**: `GenerateResumesRequestRequest`

**响应**:

  - `200`:  → `ApiGenerateResumesResp`

---

#### 🟢 GET `/api/screening/reports/{report_id}/`

**获取简历数据详情**

获取指定简历数据的详细信息

**参数**:

  - `report_id` (string, path, 必填): 

**响应**:

  - `200`:  → `ApiResumeDataDetailResp`

---

#### 🟢 GET `/api/screening/reports/{report_id}/download/`

**下载筛选报告**

下载指定简历的筛选报告（Markdown格式）

**参数**:

  - `report_id` (string, path, 必填): 

**响应**:

  - `200`:  → `any`

---

#### 🟢 GET `/api/screening/tasks/`

**获取任务历史列表**

获取筛选任务历史列表，支持分页和状态过滤

**参数**:

  - `page` (integer, query, 可选): 页码
  - `page_size` (integer, query, 可选): 每页数量
  - `status` (string, query, 可选): 状态过滤

**响应**:

  - `200`:  → `ApiTaskHistoryResp`

---

#### 🔴 DELETE `/api/screening/tasks/{task_id}/`

**删除筛选任务**

删除指定的筛选任务及其关联数据

**参数**:

  - `task_id` (string, path, 必填): 

**响应**:

  - `200`:  → `ApiTaskDeleteResp`

---

#### 🟢 GET `/api/screening/tasks/{task_id}/status/`

**获取筛选任务状态**

获取指定筛选任务的状态和结果

**参数**:

  - `task_id` (string, path, 必填): 

**响应**:

  - `200`:  → `ApiScreeningTaskStatusResp`

---

#### 🟡 POST `/api/screening/videos/link/`

**关联简历与视频**

建立简历数据与视频分析记录的关联

**请求体**: `LinkVideoRequestRequest`

**响应**:

  - `200`:  → `ApiLinkVideoResp`

---

#### 🟡 POST `/api/screening/videos/unlink/`

**解除简历与视频关联**

解除简历数据与视频分析记录的关联

**请求体**: `UnlinkVideoRequestRequest`

**响应**:

  - `200`:  → `ApiUnlinkVideoResp`

---

### 视频分析

#### 🟢 GET `/api/videos/`

**获取视频分析列表**

获取视频分析列表，支持过滤和分页

**参数**:

  - `candidate_name` (string, query, 可选): 候选人姓名过滤
  - `page` (integer, query, 可选): 页码
  - `page_size` (integer, query, 可选): 每页数量
  - `position_applied` (string, query, 可选): 应聘岗位过滤
  - `status` (string, query, 可选): 状态过滤

**响应**:

  - `200`:  → `ApiVideoListResp`

---

#### 🟡 POST `/api/videos/upload/`

**上传视频并开始分析**

上传视频文件并在后台开始分析

**响应**:

  - `201`:  → `ApiVideoUploadResp`

---

#### 🟡 POST `/api/videos/{video_id}/`

**更新视频分析结果**

更新视频分析的各项评分和状态

**参数**:

  - `video_id` (string, path, 必填): 

**请求体**: `VideoUpdateRequestRequest`

**响应**:

  - `200`:  → `ApiVideoUpdateResp`

---

#### 🟢 GET `/api/videos/{video_id}/status/`

**获取视频分析状态**

获取指定视频的分析状态和结果

**参数**:

  - `video_id` (string, path, 必填): 

**响应**:

  - `200`:  → `ApiVideoStatusResp`

---

### 最终推荐

#### 🟢 GET `/api/recommend/analysis/{resume_id}/`

**获取综合分析历史**

获取候选人的综合分析历史记录

**参数**:

  - `resume_id` (string, path, 必填): 

**响应**:

  - `200`:  → `ApiComprehensiveAnalysisGetResp`

---

#### 🟡 POST `/api/recommend/analysis/{resume_id}/`

**执行综合分析**

对单个候选人进行综合分析，整合初筛报告和面试报告

**参数**:

  - `resume_id` (string, path, 必填): 

**响应**:

  - `200`:  → `ApiComprehensiveAnalysisPostResp`

---

#### 🟢 GET `/api/recommend/stats/`

**获取推荐统计**

获取已完成综合分析的统计数据

**响应**:

  - `200`:  → `ApiRecommendStatsResp`

---

### 面试辅助

#### 🟢 GET `/api/interviews/sessions/`

**获取面试会话列表**

获取指定简历的面试会话列表

**参数**:

  - `resume_id` (string, query, 必填): 简历ID（必填）

**响应**:

  - `200`:  → `ApiSessionListResp`

---

#### 🟡 POST `/api/interviews/sessions/`

**创建面试会话**

为指定简历创建新的面试辅助会话

**请求体**: `SessionCreateRequestRequest`

**响应**:

  - `201`:  → `ApiSessionCreateResp`

---

#### 🟢 GET `/api/interviews/sessions/{session_id}/`

**获取会话详情**

获取指定面试会话的详细信息

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`:  → `ApiSessionDetailResp`

---

#### 🔴 DELETE `/api/interviews/sessions/{session_id}/`

**删除会话**

删除指定的面试会话

**参数**:

  - `session_id` (string, path, 必填): 

**响应**:

  - `200`:  → `SessionDeleteResponse`

---

#### 🟡 POST `/api/interviews/sessions/{session_id}/qa/`

**记录问答并生成候选提问**

记录面试问答，可选评估回答，并生成候选提问

**参数**:

  - `session_id` (string, path, 必填): 

**请求体**: `RecordQARequestRequest`

**响应**:

  - `200`:  → `ApiRecordQAResp`

---

#### 🟡 POST `/api/interviews/sessions/{session_id}/questions/`

**生成候选问题**

根据简历和岗位要求生成候选面试问题

**参数**:

  - `session_id` (string, path, 必填): 

**请求体**: `GenerateQuestionsRequestRequest`

**响应**:

  - `200`:  → `ApiGenerateQuestionsResp`

---

#### 🟡 POST `/api/interviews/sessions/{session_id}/report/`

**生成面试报告**

根据问答记录生成最终面试评估报告

**参数**:

  - `session_id` (string, path, 必填): 

**请求体**: `GenerateReportRequestRequest`

**响应**:

  - `200`:  → `ApiGenerateReportResp`

---

## 数据模型

以下是API中使用的主要数据结构：

### AIGenerateRequestRequest

AI生成岗位请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `description` | string | 是 | 岗位描述 |
| `documents` | any[] | 否 | 参考文档 |

### ApiAIGenerateResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | PositionItem | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiAssignResumesResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | AssignResumesResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiComprehensiveAnalysisGetResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | any | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiComprehensiveAnalysisPostResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | ComprehensiveAnalysis | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiGenerateQuestionsResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | GenerateQuestionsResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiGenerateReportResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | InterviewReportResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiGenerateResumesResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | GenerateResumesResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiLibraryBatchDeleteResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | DeletedCount | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiLibraryDetailResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | LibraryDetail | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiLibraryHashCheckResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | HashCheckResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiLibraryPaginatedResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | LibraryPaginatedData | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiLibraryUpdateResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | IdResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiLibraryUploadResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | LibraryUploadResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiLinkVideoResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | LinkVideoResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiPositionCreateResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | PositionItem | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiPositionDetailResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | PositionDetail | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiPositionListResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | PositionListData | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiPositionUpdateResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | PositionItem | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiRecommendStatsResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | RecommendStats | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiRecordQAResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | RecordQAResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiRemoveResumeResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | RemoveResumeResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiResumeDataCreateResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | IdResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiResumeDataDetailResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | ResumeDataReportWrapper | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiResumeDataListResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | ResumeDataListData | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiScreeningSubmitResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | TaskSubmit | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiScreeningTaskStatusResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | TaskStatus | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiSessionCreateResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | SessionCreateResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiSessionDetailResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | SessionDetail | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiSessionListResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | SessionItem[] | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiTaskDeleteResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | IdResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiTaskHistoryResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | TaskListData | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiUnlinkVideoResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | UnlinkVideoResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiVideoListResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | VideoListData | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiVideoStatusResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | VideoAnalysisDetail | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiVideoUpdateResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | VideoUpdateResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### ApiVideoUploadResp

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `data` | VideoUploadResponse | 是 | - |
| `code` | integer | 否 | 状态码 |
| `message` | string | 否 | 消息 |

### AssignResumesRequestRequest

分配简历请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `resume_data_ids` | string[] | 是 | 简历ID列表 |
| `notes` | string | 否 | 备注 |

### AssignResumesResponse

分配简历响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `position_id` | string | 是 | 岗位ID |
| `assigned_count` | integer | 是 | 分配数量 |
| `skipped_count` | integer | 是 | 跳过数量 |
| `total_resumes` | integer | 是 | 总简历数 |

### BatchDeleteRequestRequest

批量删除请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `resume_ids` | string[] | 是 | 简历ID列表 |

### CandidateQuestion

候选问题

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `type` | string | 是 | 问题类型 |
| `content` | string | 是 | 问题内容 |
| `reason` | string | 否 | 推荐理由 |

### ComprehensiveAnalysis

综合分析结果

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 分析ID |
| `resume_id` | string | 是 | 简历ID |
| `candidate_name` | string | 是 | 候选人姓名 |
| `final_score` | number | 是 | 最终得分 |
| `recommendation` | any | 是 | 推荐结果 |
| `dimension_scores` | any | 是 | 维度评分 |
| `comprehensive_report` | any | 是 | 综合报告 |
| `created_at` | string | 是 | 创建时间 |

### DeletedCount

删除计数响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `deleted_count` | integer | 是 | 删除数量 |

### GenerateQuestionsRequestRequest

生成问题请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `categories` | string[] | 否 | 问题类别 |
| `candidate_level` | string | 否 | 候选人级别 |
| `count_per_category` | integer | 否 | 每类问题数量 |
| `focus_on_resume` | boolean | 否 | 是否聚焦简历 |
| `interest_point_count` | integer | 否 | 兴趣点数量 |

### GenerateQuestionsResponse

生成问题响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `session_id` | string | 是 | 会话ID |
| `question_pool` | any[] | 是 | 问题池 |
| `resume_highlights` | string[] | 是 | 简历亮点 |
| `interest_points` | InterestPoint[] | 是 | 兴趣点 |

### GenerateReportRequestRequest

生成报告请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `include_conversation_log` | boolean | 否 | 包含对话记录 |
| `hr_notes` | string | 否 | HR备注 |

### GenerateResumesRequestRequest

生成简历请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `position` | any | 是 | 岗位信息 |
| `count` | integer | 否 | 生成数量 |

### GenerateResumesResponse

生成简历响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `added` | LibraryUploadItem[] | 是 | 添加的简历 |
| `skipped` | LibrarySkippedItem[] | 是 | 跳过的简历 |
| `added_count` | integer | 是 | 添加数量 |
| `skipped_count` | integer | 是 | 跳过数量 |
| `requested_count` | integer | 是 | 请求数量 |

### HashCheckRequestRequest

哈希检查请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `hashes` | string[] | 是 | 哈希值列表 |

### HashCheckResponse

哈希检查响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `exists` | object | 是 | 哈希存在映射 |
| `existing_count` | integer | 是 | 已存在数量 |

### IdResponse

ID 响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 记录ID |

### InterestPoint

兴趣点

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `content` | string | 是 | 内容 |
| `question` | string | 是 | 相关问题 |

### InterviewReportResponse

生成面试报告响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `report` | any | 是 | 报告内容 |
| `report_file_url` | string | 是 | 报告文件URL |

### LibraryDeleteResponse

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `code` | integer | 否 | - |
| `message` | string | 否 | - |
| `data` | any | 否 | - |

### LibraryDetail

简历库详情

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 简历ID |
| `filename` | string | 是 | 文件名 |
| `file_hash` | string | 是 | 文件哈希 |
| `file_size` | integer | 是 | 文件大小 |
| `file_type` | string | 是 | 文件类型 |
| `content` | string | 是 | 简历内容 |
| `candidate_name` | string | 是 | 候选人姓名 |
| `is_screened` | boolean | 是 | 是否已筛选 |
| `is_assigned` | boolean | 是 | 是否已分配 |
| `notes` | string | 是 | 备注 |
| `created_at` | string | 是 | 创建时间 |
| `updated_at` | string | 是 | 更新时间 |

### LibraryItem

简历库列表项

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 简历ID |
| `filename` | string | 是 | 文件名 |
| `file_hash` | string | 是 | 文件哈希（前8位） |
| `file_size` | integer | 是 | 文件大小 |
| `file_type` | string | 是 | 文件类型 |
| `candidate_name` | string | 是 | 候选人姓名 |
| `is_screened` | boolean | 是 | 是否已筛选 |
| `is_assigned` | boolean | 是 | 是否已分配 |
| `notes` | string | 是 | 备注 |
| `created_at` | string | 是 | 创建时间 |
| `content_preview` | string | 是 | 内容预览 |

### LibraryPaginatedData

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `items` | LibraryItem[] | 是 | - |
| `total` | integer | 是 | 总数 |
| `page` | integer | 是 | 当前页 |
| `page_size` | integer | 是 | 每页数量 |

### LibrarySkippedItem

跳过的简历项

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `filename` | string | 是 | 文件名 |
| `reason` | string | 是 | 跳过原因 |

### LibraryUpdateRequestRequest

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `candidate_name` | string | 否 | 候选人姓名 |
| `notes` | string | 否 | 备注 |

### LibraryUploadItem

上传成功的简历项

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 简历ID |
| `filename` | string | 是 | 文件名 |
| `candidate_name` | string | 是 | 候选人姓名 |

### LibraryUploadRequestRequest

简历上传请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `resumes` | any[] | 是 | 简历列表，每项包含 name, content, metadata |

### LibraryUploadResponse

简历上传响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `uploaded` | LibraryUploadItem[] | 是 | 上传成功列表 |
| `skipped` | LibrarySkippedItem[] | 是 | 跳过列表 |
| `uploaded_count` | integer | 是 | 上传成功数量 |
| `skipped_count` | integer | 是 | 跳过数量 |

### LinkVideoRequestRequest

关联视频请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `resume_data_id` | string | 是 | 简历数据ID |
| `video_analysis_id` | string | 是 | 视频分析ID |

### LinkVideoResponse

关联视频响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `resume_data_id` | string | 是 | 简历数据ID |
| `video_analysis_id` | string | 是 | 视频分析ID |
| `candidate_name` | string | 是 | 候选人姓名 |
| `video_name` | string | 是 | 视频名称 |

### PositionCreateRequestRequest

创建岗位请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `position` | string | 是 | 岗位名称 |
| `department` | string | 否 | 部门 |
| `description` | string | 否 | 岗位描述 |
| `required_skills` | string[] | 否 | 必需技能 |
| `optional_skills` | string[] | 否 | 可选技能 |
| `min_experience` | integer | 否 | 最低经验年限 |
| `education` | string[] | 否 | 学历要求 |
| `certifications` | string[] | 否 | 证书要求 |
| `salary_range` | integer[] | 否 | 薪资范围 |
| `project_requirements` | any | 否 | 项目要求 |

### PositionDeleteResponse

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `code` | integer | 否 | - |
| `message` | string | 否 | - |
| `data` | any | 否 | - |

### PositionDetail

岗位详情（含简历）

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 岗位ID |
| `position` | string | 是 | 岗位名称 |
| `department` | string | 是 | 部门 |
| `description` | string | 是 | 岗位描述 |
| `required_skills` | string[] | 是 | 必需技能 |
| `optional_skills` | string[] | 是 | 可选技能 |
| `min_experience` | integer | 是 | 最低经验年限 |
| `education` | string[] | 是 | 学历要求 |
| `certifications` | string[] | 是 | 证书要求 |
| `salary_range` | integer[] | 是 | 薪资范围 |
| `project_requirements` | any | 是 | 项目要求 |
| `resume_count` | integer | 是 | 简历数量 |
| `created_at` | string | 是 | 创建时间 |
| `resumes` | PositionResume[] | 否 | 关联简历 |

### PositionItem

岗位项

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 岗位ID |
| `position` | string | 是 | 岗位名称 |
| `department` | string | 是 | 部门 |
| `description` | string | 是 | 岗位描述 |
| `required_skills` | string[] | 是 | 必需技能 |
| `optional_skills` | string[] | 是 | 可选技能 |
| `min_experience` | integer | 是 | 最低经验年限 |
| `education` | string[] | 是 | 学历要求 |
| `certifications` | string[] | 是 | 证书要求 |
| `salary_range` | integer[] | 是 | 薪资范围 |
| `project_requirements` | any | 是 | 项目要求 |
| `resume_count` | integer | 是 | 简历数量 |
| `created_at` | string | 是 | 创建时间 |

### PositionListData

岗位列表数据

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `positions` | PositionItem[] | 是 | 岗位列表 |
| `total` | integer | 是 | 总数 |

### PositionResume

岗位关联的简历

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 简历ID |
| `candidate_name` | string | 是 | 候选人姓名 |
| `position_title` | string | 是 | 应聘岗位 |
| `resume_content` | string | 是 | 简历内容 |
| `screening_score` | any | 是 | 筛选得分 |
| `screening_summary` | string | 是 | 筛选摘要 |
| `report_md_url` | string | 是 | MD报告URL |
| `report_json_url` | string | 是 | JSON报告URL |
| `created_at` | string | 是 | 创建时间 |

### RecommendStats

推荐统计

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `analyzed_count` | integer | 是 | 已分析人数 |

### Recommendation

推荐结果

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `level` | string | 是 | 推荐等级 |
| `label` | string | 是 | 推荐标签 |
| `action` | string | 是 | 建议行动 |
| `score` | number | 是 | 推荐分数 |

### RecordQARequestRequest

记录问答请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `question` | any | 是 | 问题数据 |
| `answer` | any | 是 | 回答数据 |
| `skip_evaluation` | boolean | 否 | 跳过评估 |
| `followup_count` | integer | 否 | 追问数量 |
| `alternative_count` | integer | 否 | 候选问题数量 |

### RecordQAResponse

记录问答响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `round_number` | integer | 是 | 轮次 |
| `evaluation` | any | 是 | 评估结果 |
| `candidate_questions` | CandidateQuestion[] | 是 | 候选问题 |
| `hr_action_hints` | string[] | 是 | HR行动提示 |

### RemoveResumeResponse

移除简历响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `position_id` | string | 是 | 岗位ID |
| `resume_id` | string | 是 | 简历ID |
| `total_resumes` | integer | 是 | 剩余简历数 |

### ReportItem

报告项

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `report_id` | string | 是 | 报告ID |
| `report_filename` | string | 是 | 报告文件名 |
| `download_url` | string | 是 | 下载URL |
| `resume_content` | string | 是 | 简历内容 |

### ResumeDataCreateRequestRequest

创建简历数据请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `position_title` | string | 是 | 岗位名称 |
| `position_details` | any | 否 | 岗位详情 |
| `candidate_name` | string | 是 | 候选人姓名 |
| `resume_content` | string | 是 | 简历内容 |

### ResumeDataDetail

简历数据详情

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 简历数据ID |
| `created_at` | string | 是 | 创建时间 |
| `candidate_name` | string | 是 | 候选人姓名 |
| `position_title` | string | 是 | 应聘岗位 |
| `screening_score` | any | 是 | 筛选得分 |
| `screening_summary` | string | 是 | 筛选摘要 |
| `resume_content` | string | 是 | 简历内容 |
| `json_report_content` | any | 是 | JSON报告内容 |
| `report_json_url` | string | 是 | JSON报告URL |
| `video_analysis_id` | string | 是 | 视频分析ID |

### ResumeDataItem

简历数据项

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 简历数据ID |
| `candidate_name` | string | 是 | 候选人姓名 |
| `position_title` | string | 是 | 应聘岗位 |
| `screening_score` | any | 是 | 筛选得分 |
| `screening_summary` | string | 是 | 筛选摘要 |
| `json_content` | any | 是 | JSON内容 |
| `resume_content` | string | 是 | 简历内容 |
| `report_md_url` | string | 是 | MD报告URL |
| `report_json_url` | string | 是 | JSON报告URL |
| `video_analysis` | any | 否 | 视频分析 |

### ResumeDataList

简历数据列表项（分页用）

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 简历数据ID |
| `created_at` | string | 是 | 创建时间 |
| `position_title` | string | 是 | 应聘岗位 |
| `candidate_name` | string | 是 | 候选人姓名 |
| `screening_score` | any | 是 | 筛选得分 |
| `resume_file_hash` | string | 是 | 文件哈希 |
| `report_md_url` | string | 是 | MD报告URL |
| `report_json_url` | string | 是 | JSON报告URL |
| `video_analysis` | any | 否 | 视频分析信息 |

### ResumeDataListData

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `results` | ResumeDataList[] | 是 | - |
| `total` | integer | 是 | - |
| `page` | integer | 是 | - |
| `page_size` | integer | 是 | - |

### ResumeDataReportWrapper

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `report` | ResumeDataDetail | 是 | - |

### SessionCreateRequestRequest

创建会话请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `resume_data_id` | string | 是 | 简历数据ID |
| `job_config` | any | 否 | 岗位配置 |

### SessionCreateResponse

创建会话响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `session_id` | string | 是 | 会话ID |
| `candidate_name` | string | 是 | 候选人姓名 |
| `position_title` | string | 是 | 应聘岗位 |
| `created_at` | string | 是 | 创建时间 |
| `resume_summary` | any | 是 | 简历摘要 |

### SessionDeleteResponse

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `code` | integer | 否 | - |
| `message` | string | 否 | - |
| `data` | any | 否 | - |

### SessionDetail

会话详情

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `session_id` | string | 是 | 会话ID |
| `candidate_name` | string | 是 | 候选人姓名 |
| `position_title` | string | 是 | 应聘岗位 |
| `current_round` | integer | 是 | 当前轮次 |
| `qa_count` | integer | 是 | 问答数量 |
| `is_completed` | boolean | 是 | 是否完成 |
| `created_at` | string | 是 | 创建时间 |
| `updated_at` | string | 是 | 更新时间 |
| `has_final_report` | boolean | 否 | 是否有最终报告 |
| `final_report_summary` | string | 否 | 报告摘要 |

### SessionItem

会话列表项

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 会话ID |
| `resume_data_id` | string | 是 | 简历数据ID |
| `qa_records` | any[] | 是 | 问答记录 |
| `created_at` | string | 是 | 创建时间 |
| `final_report` | any | 否 | 最终报告 |

### TaskItem

任务项

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `task_id` | string | 是 | 任务ID |
| `status` | string | 是 | 状态

* `pending` - pending
* `running` - running
* `completed` - completed
* `failed` - failed |
| `progress` | integer | 是 | 进度 |
| `current_step` | integer | 是 | 当前步骤 |
| `total_steps` | integer | 是 | 总步骤 |
| `created_at` | string | 是 | 创建时间 |
| `current_speaker` | string | 否 | 当前发言者 |
| `resume_data` | ResumeDataItem[] | 否 | 简历数据 |
| `reports` | ReportItem[] | 否 | 报告列表 |
| `error_message` | string | 否 | 错误信息 |

### TaskListData

任务列表数据

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `tasks` | TaskItem[] | 是 | 任务列表 |
| `total` | integer | 是 | 总数 |
| `page` | integer | 是 | 当前页 |
| `page_size` | integer | 是 | 每页数量 |

### TaskStatus

任务状态响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `task_id` | string | 是 | 任务ID |
| `status` | string | 是 | 状态 |
| `progress` | integer | 是 | 进度 |
| `current_step` | integer | 是 | 当前步骤 |
| `total_steps` | integer | 是 | 总步骤 |
| `created_at` | string | 是 | 创建时间 |
| `current_speaker` | string | 否 | 当前发言者 |
| `resume_data` | ResumeDataItem[] | 否 | 简历数据 |
| `reports` | ReportItem[] | 否 | 报告列表 |
| `error_message` | string | 否 | 错误信息 |

### TaskSubmit

任务提交响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `status` | string | 是 | 状态 |
| `task_id` | string | 是 | 任务ID |

### UnlinkVideoRequestRequest

解除关联请求

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `resume_data_id` | string | 是 | 简历数据ID |

### UnlinkVideoResponse

解除关联响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `resume_data_id` | string | 是 | 简历数据ID |
| `disconnected_video_id` | string | 是 | 断开的视频ID |
| `candidate_name` | string | 是 | 候选人姓名 |
| `video_name` | string | 是 | 视频名称 |

### VideoAnalysisBrief

视频分析简要信息

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 视频分析ID |
| `video_name` | string | 是 | 视频名称 |
| `status` | string | 是 | 状态 |
| `confidence_score` | number | 是 | 置信度分数 |

### VideoAnalysisDetail

视频分析详情

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 视频分析ID |
| `video_name` | string | 是 | 视频名称 |
| `candidate_name` | string | 是 | 候选人姓名 |
| `position_applied` | string | 是 | 应聘岗位 |
| `status` | string | 是 | 状态

* `pending` - pending
* `processing` - processing
* `completed` - completed
* `failed` - failed |
| `confidence_score` | number | 是 | 置信度分数 |
| `created_at` | string | 是 | 创建时间 |
| `analysis_result` | any | 否 | 分析结果 |
| `summary` | string | 否 | 分析摘要 |
| `error_message` | string | 否 | 错误信息 |
| `resume_data_id` | string | 否 | 关联简历ID |

### VideoAnalysisItem

视频分析项

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 视频分析ID |
| `video_name` | string | 是 | 视频名称 |
| `candidate_name` | string | 是 | 候选人姓名 |
| `position_applied` | string | 是 | 应聘岗位 |
| `status` | string | 是 | 状态

* `pending` - pending
* `processing` - processing
* `completed` - completed
* `failed` - failed |
| `confidence_score` | number | 是 | 置信度分数 |
| `created_at` | string | 是 | 创建时间 |
| `analysis_result` | any | 否 | 分析结果 |

### VideoListData

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `videos` | VideoAnalysisItem[] | 是 | - |
| `total` | integer | 是 | - |
| `page` | integer | 是 | - |
| `page_size` | integer | 是 | - |

### VideoUpdateRequestRequest

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `fraud_score` | number | 否 | 欺诈评分 |
| `neuroticism_score` | number | 否 | 神经质评分 |
| `extraversion_score` | number | 否 | 外向性评分 |
| `openness_score` | number | 否 | 开放性评分 |
| `agreeableness_score` | number | 否 | 宜人性评分 |
| `conscientiousness_score` | number | 否 | 尽责性评分 |
| `summary` | string | 否 | 分析摘要 |
| `confidence_score` | number | 否 | 置信度 |
| `status` | string | 否 | 状态 |

### VideoUpdateResponse

视频更新响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 视频分析ID |
| `status` | string | 是 | 状态 |
| `analysis_result` | any | 是 | 分析结果 |
| `resume_data_id` | string | 否 | 关联简历ID |

### VideoUploadRequestRequest

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `video_file` | string | 是 | 视频文件 |
| `candidate_name` | string | 是 | 候选人姓名 |
| `position_applied` | string | 是 | 应聘岗位 |
| `resume_data_id` | string | 否 | 关联简历ID |
| `video_name` | string | 否 | 视频名称 |

### VideoUploadResponse

视频上传响应

| 字段 | 类型 | 必填 | 说明 |
|:-----|:-----|:-----|:-----|
| `id` | string | 是 | 视频分析ID |
| `video_name` | string | 是 | 视频名称 |
| `candidate_name` | string | 是 | 候选人姓名 |
| `position_applied` | string | 是 | 应聘岗位 |
| `status` | string | 是 | 状态 |
| `created_at` | string | 是 | 创建时间 |
| `resume_data_id` | string | 否 | 关联简历ID |
