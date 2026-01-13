# EV Test Platform - 新能源汽车测试平台

<div align="center">

![EV Test Platform](https://img.shields.io/badge/EV%20Test%20Platform-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18+-61DAFB)
![License](https://img.shields.io/badge/License-MIT-yellow)

**面向新能源汽车研发团队的一站式自动化测试管理平台**

</div>

---

## 📖 项目简介

EV Test Platform 是一个专为新能源汽车领域设计的综合测试管理平台，提供测试任务调度、环境管理、测试报告等核心功能，帮助测试团队提高效率、保证质量。

### 核心功能

- 🚀 **测试任务管理** - 支持立即执行、定时执行、周期执行
- 🖥️ **测试环境管理** - 管理测试主机、测试设备、环境组合
- 📊 **测试报告** - 自动生成报告，支持趋势分析
- 🔗 **系统集成** - 集成 ALM、GitLab、制品库
- ⬆️ **版本升级** - 支持从制品库获取版本并升级设备

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                           用户层                                     │
│  Web UI │ API │ CI/CD │ ALM │ 消息通知                               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           应用层                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │ FastAPI     │  │ React +     │  │ Celery      │                 │
│  │ Backend     │  │ TypeScript  │  │ Workers     │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          中间件层                                    │
│  PostgreSQL │ Redis │ RabbitMQ │ MinIO                              │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         执行节点层                                   │
│  Test Agent → Test Host → Test Device (ECU/VCU/BMS/MCU)             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
ev-test-platform/
├── backend/                    # 后端服务 (FastAPI)
│   ├── app/
│   │   ├── api/               # API接口
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic模式
│   │   ├── services/          # 业务逻辑
│   │   └── workers/           # Celery任务
│   ├── main.py               # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # 前端应用 (React)
│   ├── src/
│   │   ├── components/        # 通用组件
│   │   ├── layouts/           # 布局组件
│   │   ├── pages/             # 页面组件
│   │   ├── services/          # API服务
│   │   └── stores/            # 状态管理
│   ├── package.json
│   └── Dockerfile
│
├── deploy/                     # 部署配置
│   ├── docker-compose.yml
│   └── nginx/
│
└── docs/                       # 文档
    ├── 01-PRD-产品需求文档.md
    ├── 02-系统架构设计.md
    ├── 03-数据库设计.md
    └── 04-API接口设计.md
```

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 1. 使用 Docker Compose 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/your-repo/ev-test-platform.git
cd ev-test-platform

# 启动所有服务
cd deploy
docker-compose up -d

# 查看服务状态
docker-compose ps
```

服务启动后：
- 前端界面: http://localhost:3000
- API文档: http://localhost:8000/docs
- MinIO控制台: http://localhost:9001
- RabbitMQ管理: http://localhost:15672

### 2. 本地开发

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库等

# 运行开发服务器
uvicorn main:app --reload --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

---

## 📚 主要功能

### 测试任务管理

| 功能 | 描述 |
|------|------|
| 任务创建 | 手动创建、ALM同步、API创建 |
| 任务调度 | 立即执行、定时执行、CRON周期执行 |
| 任务队列 | 优先级队列，自动分配环境 |
| 版本升级 | 从制品库获取版本，升级测试设备 |

### 测试环境管理

| 功能 | 描述 |
|------|------|
| 主机管理 | SSH连接、状态监控、能力标签 |
| 设备管理 | ECU/VCU/BMS等设备管理 |
| 环境组合 | 主机+设备组合，统一管理 |
| 环境预约 | 支持预约特定时间段 |

### 测试报告

| 功能 | 描述 |
|------|------|
| 报告生成 | 自动生成HTML/PDF/JSON报告 |
| 统计分析 | 通过率趋势、失败分析 |
| 报告导出 | 支持多种格式导出 |

---

## 🔌 API 示例

### 创建测试任务

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "VCU回归测试",
    "trigger_type": "immediate",
    "need_upgrade": true,
    "version_config": {"strategy": "latest"},
    "test_config": {"suite_id": "uuid"}
  }'
```

### 查看任务状态

```bash
curl http://localhost:8000/api/v1/tasks/{task_id} \
  -H "Authorization: Bearer <token>"
```

详细API文档请参考: [API接口设计](docs/04-API接口设计.md)

---

## 🔧 配置说明

### 环境变量

| 变量 | 描述 | 默认值 |
|------|------|--------|
| DATABASE_URL | 数据库连接地址 | - |
| REDIS_URL | Redis连接地址 | - |
| SECRET_KEY | JWT密钥 | - |
| GITLAB_URL | GitLab地址 | - |
| ALM_URL | ALM平台地址 | - |

详细配置请参考 `.env.example`

---

## 📖 文档

- [产品需求文档](docs/01-PRD-产品需求文档.md)
- [系统架构设计](docs/02-系统架构设计.md)
- [数据库设计](docs/03-数据库设计.md)
- [API接口设计](docs/04-API接口设计.md)

---

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy
- **缓存**: Redis
- **任务队列**: Celery + RabbitMQ
- **存储**: MinIO

### 前端
- **框架**: React 18 + TypeScript
- **UI库**: Ant Design 5
- **图表**: ECharts
- **状态管理**: Zustand
- **构建**: Vite

---

## 📈 Roadmap

- [x] 核心功能开发
- [x] 基础UI界面
- [ ] WebSocket实时日志
- [ ] 更多设备协议支持 (CAN, UDS, DoIP)
- [ ] 移动端适配
- [ ] 多租户支持
- [ ] 高可用部署方案

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 📞 联系我们

如有问题或建议，请提交 Issue 或联系维护团队。
