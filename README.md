# Campsite Search & Monitoring System

一个全功能的营地搜索和自动监控系统，帮助你找到并预订心仪的营地。

## 🌟 主要功能

### ✅ 即时搜索
- 搜索多个营地供应商（RecreationDotGov, ReserveCalifornia 等）
- 检查特定日期的营地可用性
- 多营地批量搜索
- 精确日期和范围搜索模式

### ✅ 自动监控
- 创建监控任务，自动检查营地可用性
- 后台任务队列处理
- 用户认证和授权（JWT）
- 任务状态管理（活跃、暂停、完成、取消）
- 通知历史记录

### ✅ 管理界面
- React 前端用户界面
- 用户认证系统
- 监控任务管理
- Admin 后台监控

## 🏗️ 技术栈

**后端：**
- Python 3.12+
- FastAPI (REST API)
- PostgreSQL 15 (数据库)
- Redis (缓存/队列)
- RQ (后台任务队列)
- SQLAlchemy 2.0 (ORM)
- Alembic (数据库迁移)
- Camply CLI (营地数据源)

**前端：**
- React 18
- React Router
- Axios

## 📁 项目结构

```
campsite-search-resevation/
├── backend/                      # Python FastAPI 后端
│   ├── app/                      # 应用核心代码
│   │   ├── main.py               # FastAPI 主应用
│   │   ├── database.py           # 数据库配置
│   │   ├── db_models.py          # SQLAlchemy 模型
│   │   ├── auth.py               # JWT 认证
│   │   ├── tasks.py              # RQ 后台任务
│   │   ├── providers/            # 营地供应商集成
│   │   └── routers/              # API 路由
│   ├── alembic/                  # 数据库迁移
│   ├── logs/                     # 日志文件
│   ├── start_infrastructure.sh   # 启动基础设施
│   ├── start_api.sh              # 启动 API 服务器
│   ├── start_worker.sh           # 启动 RQ Worker
│   ├── stop_services.sh          # 停止服务
│   └── 📚 文档/
│       ├── README.md             # 后端文档
│       ├── DEVELOPER.md          # 开发者指南 ⭐
│       ├── API_USAGE.md          # API 使用文档
│       └── DESIGN.md             # 系统设计文档
│
└── frontend/                     # React 前端
    ├── src/
    │   ├── App.js                # 主应用
    │   ├── Login.js              # 登录页面
    │   ├── Register.js           # 注册页面
    │   ├── TaskList.js           # 任务列表
    │   └── AdminDashboard.js     # 管理后台
    └── public/
```

## 🚀 快速开始

### 前提条件

- Python 3.12+
- PostgreSQL 15
- Redis
- Node.js 16+
- Homebrew (macOS)

### 1. 安装后端服务

```bash
cd backend
./setup_services.sh
```

这会自动安装 PostgreSQL、Redis，创建数据库并配置环境。

### 2. 启动后端服务

**推荐方式（3个终端窗口）：**

终端 1 - 基础设施：
```bash
cd backend
./start_infrastructure.sh
```

终端 2 - API 服务器：
```bash
cd backend
./start_api.sh
```

终端 3 - 后台任务处理器：
```bash
cd backend
./start_worker.sh
```

**优势：**
- ✅ 实时查看日志
- ✅ 避免 camply 输出格式问题
- ✅ 方便调试

### 3. 启动前端

打开新终端窗口：

```bash
cd frontend
npm install
npm start
```

访问 http://localhost:3000

### 4. 访问服务

- **前端界面**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 5. 停止服务

```bash
cd backend
./stop_services.sh
```

## 📖 使用示例

### 用户注册和登录

```bash
# 注册用户
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'

# 登录获取 token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}'
```

### 创建监控任务

```bash
curl -X POST http://localhost:8000/monitoring/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "provider": "RecreationDotGov",
    "campground_id": "232448",
    "campground_name": "Upper Pines Campground",
    "start_date": "2026-07-01",
    "end_date": "2026-07-05",
    "search_mode": "exact"
  }'
```

更多示例请查看 [backend/API_USAGE.md](./backend/API_USAGE.md)

## 📚 完整文档

### 入门文档
- [backend/README.md](./backend/README.md) - 后端项目概览
- [backend/DEVELOPER.md](./backend/DEVELOPER.md) - **开发者指南（启动脚本、调试）** ⭐ 必读

### 使用文档
- [backend/API_USAGE.md](./backend/API_USAGE.md) - API 使用示例
- [backend/DESIGN.md](./backend/DESIGN.md) - 系统设计文档

## 🏗️ 系统架构

```
┌──────────┐
│  用户    │
└────┬─────┘
     │ HTTP/REST
     ▼
┌──────────────┐
│  React       │  前端界面
│  Frontend    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  FastAPI     │ ──► PostgreSQL (数据存储)
│  API Server  │
└──────┬───────┘
       │ 创建任务
       ▼
┌──────────────┐
│    Redis     │ ◄── 消息队列
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  RQ Worker   │ ──► Camply (检查可用性)
│  后台任务    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  通知记录    │ ──► PostgreSQL
└──────────────┘
```

## 🗄️ 数据库设计

主要表结构：

- **users** - 用户账户
- **monitoring_tasks** - 监控任务
- **notification_history** - 通知历史
- **notification_settings** - 通知配置
- **favorite_campgrounds** - 收藏营地

详细设计请查看 [backend/DESIGN.md](./backend/DESIGN.md)

## 🔐 安全性

- 密码安全：bcrypt 哈希
- 认证：JWT Token (30分钟有效期)
- 授权：基于用户的资源隔离
- SQL 注入防护：SQLAlchemy ORM 参数化查询
- 环境变量：敏感信息存储在 `.env`

## 🐛 常见问题

### 后端启动问题

**端口被占用：**
```bash
lsof -ti:8000 | xargs kill -9
```

**PostgreSQL 未运行：**
```bash
brew services start postgresql@15
```

**Redis 未运行：**
```bash
brew services start redis
```

### Camply 解析错误

如果遇到 `ValueError: invalid literal for int()` 错误，请使用推荐的前台启动方式（3个终端窗口）。

详细说明请查看 [backend/DEVELOPER.md](./backend/DEVELOPER.md)

## 🔮 未来计划

### Phase 2
- [ ] Email 通知支持
- [ ] Pushover 通知支持
- [ ] 定时调度（每小时自动检查）

### Phase 3
- [ ] WebSocket 实时通知
- [ ] 营地收藏功能增强
- [ ] 移动端适配

### Phase 4
- [ ] 多用户协作
- [ ] 营地推荐系统
- [ ] 价格追踪

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题，请查阅文档或提交 Issue。

---

**开始使用：**
1. 运行 `cd backend && ./setup_services.sh` 安装
2. 运行 `./start_infrastructure.sh` 启动基础设施
3. 在两个终端分别运行 `./start_api.sh` 和 `./start_worker.sh`
4. 运行 `cd ../frontend && npm install && npm start` 启动前端
5. 访问 http://localhost:3000 开始使用
6. 阅读 [backend/DEVELOPER.md](./backend/DEVELOPER.md) 了解详细信息
