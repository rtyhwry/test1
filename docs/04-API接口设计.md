# 新能源汽车测试平台 - API接口设计

## 1. API设计规范

### 1.1 基础规范

| 项目 | 规范 |
|------|------|
| 协议 | HTTPS |
| 风格 | RESTful |
| 版本 | URL路径版本 (/api/v1) |
| 认证 | JWT Bearer Token |
| 格式 | JSON |
| 编码 | UTF-8 |
| 时间 | ISO 8601 (UTC) |

### 1.2 请求格式
```http
POST /api/v1/tasks HTTP/1.1
Host: api.evtest.example.com
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "示例任务",
  "project_id": "uuid"
}
```

### 1.3 响应格式

#### 成功响应
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "name": "示例任务"
  },
  "timestamp": "2026-01-13T10:00:00Z"
}
```

#### 分页响应
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "timestamp": "2026-01-13T10:00:00Z"
}
```

#### 错误响应
```json
{
  "code": 40001,
  "message": "参数验证失败",
  "errors": [
    {
      "field": "name",
      "message": "名称不能为空"
    }
  ],
  "timestamp": "2026-01-13T10:00:00Z"
}
```

### 1.4 错误码规范

| 错误码范围 | 类型 | 说明 |
|-----------|------|------|
| 0 | 成功 | 请求成功 |
| 40001-40099 | 参数错误 | 请求参数验证失败 |
| 40101-40199 | 认证错误 | 未登录或Token无效 |
| 40301-40399 | 权限错误 | 无操作权限 |
| 40401-40499 | 资源错误 | 资源不存在 |
| 40901-40999 | 冲突错误 | 资源状态冲突 |
| 50001-50099 | 服务错误 | 服务内部错误 |
| 50201-50299 | 外部错误 | 外部服务调用失败 |

---

## 2. 认证接口

### 2.1 用户登录

#### POST /api/v1/auth/login
登录获取Token

**请求体:**
```json
{
  "username": "admin",
  "password": "password123",
  "login_type": "local"  // local, ldap
}
```

**响应:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "display_name": "管理员"
    }
  }
}
```

### 2.2 刷新Token

#### POST /api/v1/auth/refresh
刷新访问Token

**请求体:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### 2.3 登出

#### POST /api/v1/auth/logout
登出并使Token失效

### 2.4 获取当前用户信息

#### GET /api/v1/auth/me
获取当前登录用户信息

---

## 3. 项目管理接口

### 3.1 项目列表

#### GET /api/v1/projects
获取项目列表

**查询参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |
| status | string | 否 | 状态筛选 |
| keyword | string | 否 | 关键词搜索 |

### 3.2 创建项目

#### POST /api/v1/projects
创建新项目

**请求体:**
```json
{
  "name": "项目名称",
  "code": "PROJECT001",
  "description": "项目描述",
  "owner_id": "uuid"
}
```

### 3.3 获取项目详情

#### GET /api/v1/projects/{project_id}

### 3.4 更新项目

#### PUT /api/v1/projects/{project_id}

### 3.5 删除项目

#### DELETE /api/v1/projects/{project_id}

---

## 4. 测试任务接口

### 4.1 任务列表

#### GET /api/v1/tasks
获取测试任务列表

**查询参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | uuid | 否 | 项目ID |
| status | string | 否 | 状态: pending, queued, running, success, failed |
| trigger_type | string | 否 | 触发类型: immediate, scheduled, cron |
| source | string | 否 | 来源: manual, alm, ci |
| created_by | uuid | 否 | 创建人 |
| start_date | datetime | 否 | 开始日期 |
| end_date | datetime | 否 | 结束日期 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "回归测试-VCU",
        "project": {
          "id": "uuid",
          "name": "VCU项目"
        },
        "source": "manual",
        "trigger_type": "immediate",
        "priority": 5,
        "status": "running",
        "progress": 45,
        "environment": {
          "id": "uuid",
          "name": "HIL环境1"
        },
        "statistics": {
          "total_cases": 100,
          "passed": 40,
          "failed": 5,
          "running": 1,
          "pending": 54
        },
        "created_by": {
          "id": "uuid",
          "username": "admin"
        },
        "created_at": "2026-01-13T08:00:00Z",
        "started_at": "2026-01-13T08:05:00Z"
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20
  }
}
```

### 4.2 创建任务

#### POST /api/v1/tasks
创建测试任务

**请求体:**
```json
{
  "name": "VCU回归测试",
  "description": "版本1.2.0回归测试",
  "project_id": "uuid",
  
  "trigger_type": "immediate",
  // 或定时执行
  // "trigger_type": "scheduled",
  // "schedule_time": "2026-01-14T02:00:00Z",
  // 或CRON表达式
  // "trigger_type": "cron",
  // "cron_expression": "0 2 * * *",
  
  "priority": 5,
  
  "need_upgrade": true,
  "version_config": {
    "strategy": "specific",  // latest, specific
    "version": "1.2.0",
    "artifact_name": "VCU_Firmware"
  },
  
  "env_config": {
    "strategy": "auto",  // auto, specific
    "environment_id": null,
    "requirements": {
      "device_type": "VCU",
      "capabilities": ["CAN", "UDS"]
    }
  },
  
  "test_config": {
    "suite_id": "uuid",
    "case_ids": null,  // null表示全部用例
    "case_filter": {
      "priority": ["critical", "high"],
      "tags": ["smoke"]
    }
  },
  
  "execution_config": {
    "timeout": 7200,
    "retry_on_failure": true,
    "max_retries": 2
  },
  
  "notify_config": {
    "on_success": true,
    "on_failure": true,
    "channels": ["email", "webhook"],
    "recipients": ["user@example.com"],
    "webhook_url": "https://webhook.example.com/notify"
  }
}
```

**响应:**
```json
{
  "code": 0,
  "data": {
    "id": "uuid",
    "name": "VCU回归测试",
    "status": "pending",
    "created_at": "2026-01-13T10:00:00Z"
  }
}
```

### 4.3 获取任务详情

#### GET /api/v1/tasks/{task_id}

**响应:**
```json
{
  "code": 0,
  "data": {
    "id": "uuid",
    "name": "VCU回归测试",
    "description": "版本1.2.0回归测试",
    "project": {
      "id": "uuid",
      "name": "VCU项目"
    },
    "source": "manual",
    "trigger_type": "immediate",
    "priority": 5,
    "status": "running",
    
    "upgrade_info": {
      "need_upgrade": true,
      "target_version": "1.2.0",
      "current_version": "1.1.0",
      "upgrade_status": "completed"
    },
    
    "environment": {
      "id": "uuid",
      "name": "HIL环境1",
      "host": {
        "id": "uuid",
        "name": "测试主机1",
        "ip": "192.168.1.100"
      },
      "device": {
        "id": "uuid",
        "name": "VCU-001",
        "type": "VCU"
      }
    },
    
    "test_suite": {
      "id": "uuid",
      "name": "VCU功能测试套件",
      "git_repo": "https://gitlab.example.com/tests/vcu.git"
    },
    
    "execution": {
      "id": "uuid",
      "number": 1,
      "git_commit": "abc123",
      "started_at": "2026-01-13T08:05:00Z",
      "duration": 1800
    },
    
    "statistics": {
      "total_cases": 100,
      "passed": 40,
      "failed": 5,
      "skipped": 0,
      "error": 0,
      "running": 1,
      "pending": 54,
      "pass_rate": 88.89
    },
    
    "created_by": {
      "id": "uuid",
      "username": "admin"
    },
    "created_at": "2026-01-13T08:00:00Z",
    "started_at": "2026-01-13T08:05:00Z"
  }
}
```

### 4.4 更新任务

#### PUT /api/v1/tasks/{task_id}
更新任务配置（仅pending状态可更新）

### 4.5 删除任务

#### DELETE /api/v1/tasks/{task_id}

### 4.6 执行任务操作

#### POST /api/v1/tasks/{task_id}/actions
对任务执行操作

**请求体:**
```json
{
  "action": "start"  // start, stop, cancel, retry
}
```

### 4.7 获取任务执行日志

#### GET /api/v1/tasks/{task_id}/logs
获取任务执行日志

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| execution_id | uuid | 执行ID |
| level | string | 日志级别: debug, info, warning, error |
| start_time | datetime | 开始时间 |
| limit | int | 返回条数 |

### 4.8 获取任务执行历史

#### GET /api/v1/tasks/{task_id}/executions
获取任务的执行历史列表

### 4.9 获取用例执行结果

#### GET /api/v1/tasks/{task_id}/executions/{execution_id}/results
获取某次执行的用例结果

---

## 5. 测试环境接口

### 5.1 环境列表

#### GET /api/v1/environments

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| project_id | uuid | 项目ID |
| status | string | 状态: idle, busy, offline, maintenance |
| env_type | string | 类型: HIL, SIL |
| capabilities | string | 能力标签(逗号分隔) |

**响应:**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "HIL环境1",
        "env_type": "HIL",
        "status": "idle",
        "host": {
          "id": "uuid",
          "name": "测试主机1",
          "ip": "192.168.1.100",
          "status": "online"
        },
        "devices": [
          {
            "id": "uuid",
            "name": "VCU-001",
            "type": "VCU",
            "current_version": "1.2.0",
            "status": "online"
          }
        ],
        "capabilities": ["CAN", "UDS", "DoIP"],
        "current_task": null,
        "last_used_at": "2026-01-13T06:00:00Z"
      }
    ],
    "total": 10
  }
}
```

### 5.2 创建环境

#### POST /api/v1/environments

**请求体:**
```json
{
  "name": "HIL环境1",
  "description": "VCU测试环境",
  "env_type": "HIL",
  "project_id": "uuid",
  "host_id": "uuid",
  "device_ids": ["uuid1", "uuid2"],
  "capabilities": ["CAN", "UDS"],
  "tags": ["VCU", "生产环境"]
}
```

### 5.3 获取环境详情

#### GET /api/v1/environments/{env_id}

### 5.4 更新环境

#### PUT /api/v1/environments/{env_id}

### 5.5 删除环境

#### DELETE /api/v1/environments/{env_id}

### 5.6 环境操作

#### POST /api/v1/environments/{env_id}/actions

**请求体:**
```json
{
  "action": "maintenance"  // maintenance, release, reserve
}
```

### 5.7 预约环境

#### POST /api/v1/environments/{env_id}/reserve

**请求体:**
```json
{
  "start_time": "2026-01-14T08:00:00Z",
  "end_time": "2026-01-14T18:00:00Z",
  "reason": "重要版本测试"
}
```

---

## 6. 测试主机接口

### 6.1 主机列表

#### GET /api/v1/hosts

### 6.2 创建主机

#### POST /api/v1/hosts

**请求体:**
```json
{
  "name": "测试主机1",
  "description": "VCU测试主机",
  "ip_address": "192.168.1.100",
  "ssh_port": 22,
  "username": "testuser",
  "auth_type": "password",
  "password": "encrypted_password",
  "work_directory": "/opt/test",
  "project_id": "uuid",
  "capabilities": ["python3", "pytest"],
  "max_concurrent_tasks": 2
}
```

### 6.3 测试连接

#### POST /api/v1/hosts/{host_id}/test-connection
测试主机连接

### 6.4 获取主机系统信息

#### GET /api/v1/hosts/{host_id}/system-info

---

## 7. 测试设备接口

### 7.1 设备列表

#### GET /api/v1/devices

### 7.2 创建设备

#### POST /api/v1/devices

**请求体:**
```json
{
  "name": "VCU-001",
  "description": "整车控制器",
  "device_type": "VCU",
  "model": "VCU-V2.0",
  "serial_number": "SN12345678",
  "host_id": "uuid",
  "connection_type": "can",
  "connection_config": {
    "channel": "can0",
    "bitrate": 500000
  },
  "project_id": "uuid",
  "capabilities": ["UDS", "DoIP"]
}
```

### 7.3 设备升级

#### POST /api/v1/devices/{device_id}/upgrade

**请求体:**
```json
{
  "artifact_id": "uuid",
  // 或
  "version": "1.2.0"
}
```

### 7.4 获取设备版本信息

#### GET /api/v1/devices/{device_id}/version

---

## 8. 测试套件和用例接口

### 8.1 套件列表

#### GET /api/v1/test-suites

### 8.2 创建套件

#### POST /api/v1/test-suites

**请求体:**
```json
{
  "name": "VCU功能测试套件",
  "description": "VCU完整功能测试",
  "project_id": "uuid",
  "source": "gitlab",
  "git_repo": "https://gitlab.example.com/tests/vcu.git",
  "git_branch": "main",
  "git_path": "tests/",
  "framework": "pytest",
  "setup_commands": "pip install -r requirements.txt",
  "teardown_commands": ""
}
```

### 8.3 同步套件用例

#### POST /api/v1/test-suites/{suite_id}/sync
从GitLab或ALM同步测试用例

### 8.4 获取套件用例

#### GET /api/v1/test-suites/{suite_id}/cases

### 8.5 用例列表

#### GET /api/v1/test-cases

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| suite_id | uuid | 套件ID |
| priority | string | 优先级 |
| tags | string | 标签(逗号分隔) |
| keyword | string | 关键词搜索 |

---

## 9. 测试报告接口

### 9.1 报告列表

#### GET /api/v1/reports

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| project_id | uuid | 项目ID |
| task_id | uuid | 任务ID |
| start_date | date | 开始日期 |
| end_date | date | 结束日期 |

### 9.2 获取报告详情

#### GET /api/v1/reports/{report_id}

**响应:**
```json
{
  "code": 0,
  "data": {
    "id": "uuid",
    "task": {
      "id": "uuid",
      "name": "VCU回归测试"
    },
    "execution": {
      "id": "uuid",
      "number": 1
    },
    "summary": {
      "total_cases": 100,
      "passed": 95,
      "failed": 3,
      "skipped": 2,
      "error": 0,
      "pass_rate": 96.94,
      "duration": 3600
    },
    "environment_info": {
      "host": "测试主机1",
      "device": "VCU-001",
      "software_version": "1.2.0"
    },
    "failed_cases": [
      {
        "id": "uuid",
        "name": "test_power_on",
        "error_message": "Timeout waiting for response",
        "duration": 30000
      }
    ],
    "duration_distribution": {
      "0-1s": 50,
      "1-5s": 30,
      "5-10s": 15,
      "10s+": 5
    },
    "created_at": "2026-01-13T10:00:00Z"
  }
}
```

### 9.3 导出报告

#### GET /api/v1/reports/{report_id}/export

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| format | string | 导出格式: pdf, excel, html |

### 9.4 获取统计数据

#### GET /api/v1/reports/statistics

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| project_id | uuid | 项目ID |
| period | string | 时间段: day, week, month |
| start_date | date | 开始日期 |
| end_date | date | 结束日期 |

**响应:**
```json
{
  "code": 0,
  "data": {
    "overview": {
      "total_tasks": 150,
      "total_executions": 200,
      "total_cases": 5000,
      "avg_pass_rate": 95.5
    },
    "trend": [
      {
        "date": "2026-01-07",
        "executions": 30,
        "pass_rate": 94.5
      },
      {
        "date": "2026-01-08",
        "executions": 28,
        "pass_rate": 96.2
      }
    ],
    "by_project": [
      {
        "project_id": "uuid",
        "project_name": "VCU项目",
        "executions": 80,
        "pass_rate": 97.0
      }
    ],
    "top_failed_cases": [
      {
        "case_id": "uuid",
        "case_name": "test_power_on",
        "failure_count": 5
      }
    ]
  }
}
```

---

## 10. 集成接口

### 10.1 ALM同步

#### POST /api/v1/integrations/alm/sync
从ALM平台同步测试任务

**请求体:**
```json
{
  "alm_project_id": "123",
  "sync_type": "tasks",  // tasks, cases
  "filter": {
    "status": "ready",
    "priority": ["high", "critical"]
  }
}
```

### 10.2 GitLab Webhook

#### POST /api/v1/integrations/gitlab/webhook
接收GitLab事件通知

### 10.3 制品库版本查询

#### GET /api/v1/integrations/artifact/versions

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| name | string | 制品名称 |
| device_type | string | 设备类型 |

### 10.4 通知测试

#### POST /api/v1/integrations/notification/test
测试通知配置

---

## 11. WebSocket接口

### 11.1 连接地址
```
wss://api.evtest.example.com/api/v1/ws?token=<jwt_token>
```

### 11.2 消息格式

#### 订阅消息
```json
{
  "type": "subscribe",
  "channel": "task",
  "id": "task_uuid"
}
```

#### 任务状态更新
```json
{
  "type": "task_status",
  "data": {
    "task_id": "uuid",
    "status": "running",
    "progress": 45,
    "current_case": "test_power_on"
  }
}
```

#### 日志推送
```json
{
  "type": "task_log",
  "data": {
    "task_id": "uuid",
    "level": "info",
    "message": "用例 test_power_on 开始执行",
    "timestamp": "2026-01-13T10:00:00Z"
  }
}
```

#### 环境状态更新
```json
{
  "type": "env_status",
  "data": {
    "env_id": "uuid",
    "status": "busy",
    "current_task_id": "uuid"
  }
}
```

---

## 12. 系统管理接口

### 12.1 用户管理

#### GET /api/v1/admin/users
获取用户列表

#### POST /api/v1/admin/users
创建用户

#### PUT /api/v1/admin/users/{user_id}
更新用户

#### DELETE /api/v1/admin/users/{user_id}
删除用户

### 12.2 角色管理

#### GET /api/v1/admin/roles
#### POST /api/v1/admin/roles
#### PUT /api/v1/admin/roles/{role_id}

### 12.3 集成配置

#### GET /api/v1/admin/integrations
#### POST /api/v1/admin/integrations
#### PUT /api/v1/admin/integrations/{id}
#### DELETE /api/v1/admin/integrations/{id}

### 12.4 系统配置

#### GET /api/v1/admin/settings
#### PUT /api/v1/admin/settings

### 12.5 操作日志

#### GET /api/v1/admin/audit-logs

---

## 13. 健康检查接口

### 13.1 健康检查

#### GET /api/v1/health

**响应:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-13T10:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "rabbitmq": "healthy",
    "storage": "healthy"
  }
}
```

### 13.2 就绪检查

#### GET /api/v1/ready

---

## 14. API调用示例

### 14.1 创建并执行测试任务

```bash
# 1. 登录获取Token
curl -X POST https://api.evtest.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# 2. 创建测试任务
curl -X POST https://api.evtest.example.com/api/v1/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "VCU回归测试",
    "project_id": "uuid",
    "trigger_type": "immediate",
    "need_upgrade": true,
    "version_config": {"strategy": "latest"},
    "test_config": {"suite_id": "uuid"}
  }'

# 3. 查看任务状态
curl https://api.evtest.example.com/api/v1/tasks/{task_id} \
  -H "Authorization: Bearer <token>"

# 4. 获取测试报告
curl https://api.evtest.example.com/api/v1/reports?task_id={task_id} \
  -H "Authorization: Bearer <token>"
```

### 14.2 Python SDK示例

```python
from evtest_sdk import EVTestClient

# 初始化客户端
client = EVTestClient(
    base_url="https://api.evtest.example.com",
    username="admin",
    password="password"
)

# 创建测试任务
task = client.tasks.create(
    name="VCU回归测试",
    project_id="uuid",
    trigger_type="immediate",
    need_upgrade=True,
    version_config={"strategy": "latest"},
    test_config={"suite_id": "uuid"}
)

# 等待任务完成
task.wait_until_complete(timeout=3600)

# 获取报告
report = client.reports.get_by_task(task.id)
print(f"通过率: {report.pass_rate}%")
```
