# Campsite Search & Monitoring System

一个全功能的营地搜索和监控系统，支持即时搜索和自动化监控通知。

## 🌟 功能特性

### 即时搜索
- ✅ 搜索多个营地供应商（RecreationDotGov, ReserveCalifornia 等）
- ✅ 检查特定日期的营地可用性
- ✅ 多营地批量搜索
- ✅ 精确日期和范围搜索模式

### 自动监控（新功能）
- ✅ 创建监控任务，自动检查营地可用性
- ✅ 后台任务队列处理
- ✅ 用户认证和授权（JWT）
- ✅ 任务状态管理（活跃、暂停、完成、取消）
- ✅ 通知历史记录
- 🔜 Email/Pushover 通知（即将推出）

## 🏗️ 技术栈

- **后端框架**: FastAPI (Python 3.12+)
- **数据库**: PostgreSQL 15
- **缓存/队列**: Redis
- **任务队列**: RQ (Redis Queue)
- **认证**: JWT (JSON Web Tokens)
- **ORM**: SQLAlchemy 2.0
- **数据库迁移**: Alembic
- **营地数据源**: Camply CLI

## 📁 项目结构

```
backend/
├── app/                          # 应用核心代码
│   ├── main.py                   # FastAPI 主应用
│   ├── database.py               # 数据库配置
│   ├── db_models.py              # SQLAlchemy 模型
│   ├── auth.py                   # JWT 认证
│   ├── tasks.py                  # RQ 后台任务
│   ├── scheduler.py              # 任务调度器
│   ├── providers/                # 营地供应商集成
│   └── routers/                  # API 路由
│       ├── auth.py               # 认证路由
│       └── monitoring.py         # 监控任务路由
│
├── alembic/                      # 数据库迁移
├── logs/                         # 日志文件
├── .env                          # 环境变量
├── requirements.txt              # Python 依赖
│
├── setup_services.sh             # 一键安装脚本
├── start_services.sh             # 启动服务脚本
├── stop_services.sh              # 停止服务脚本
│
└── 📚 文档/
    ├── README.md                 # 本文档
    ├── SETUP_INSTRUCTIONS.md     # 安装指南
    ├── API_USAGE.md              # API 使用文档
    ├── DEVELOPER.md              # 开发者文档
    └── DESIGN.md                 # 系统设计文档
```

## 🚀 快速开始

### 1. 安装服务

```bash
cd backend
./setup_services.sh
```

这会自动安装 PostgreSQL、Redis，创建数据库并配置环境。

### 2. 启动服务

```bash
./start_services.sh
```

启动 FastAPI 服务器和 RQ Worker。

### 3. 访问 API

- **API 服务**: http://localhost:8000
- **交互式文档**: http://localhost:8000/docs

### 4. 停止服务

```bash
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

# 响应
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
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

### 查看所有任务

```bash
curl http://localhost:8000/monitoring/tasks \
  -H "Authorization: Bearer <your_token>"
```

更多示例请查看 [API_USAGE.md](./API_USAGE.md)

## 🔍 监控和调试

### 查看数据库

```bash
# 连接数据库
psql campsite_db

# 查看所有表
\dt

# 查看监控任务
SELECT id, campground_name, status, created_at
FROM monitoring_tasks
ORDER BY created_at DESC
LIMIT 10;
```

### 查看 Redis 队列

```bash
# 连接 Redis
redis-cli

# 查看队列长度
LLEN rq:queue:monitoring

# 查看所有键
KEYS rq:*
```

### 查看 RQ 任务状态

```bash
# 使用 RQ CLI
./campsite-env/bin/rq info --url redis://localhost:6379/0

# 安装并启动 RQ Dashboard
./campsite-env/bin/pip install rq-dashboard
./campsite-env/bin/rq-dashboard --redis-url redis://localhost:6379/0
# 访问 http://localhost:9181
```

### 查看日志

```bash
# API 服务器日志
tail -f logs/api_server.log

# RQ Worker 日志
tail -f logs/rq_worker.log
```

详细调试指南请查看 [DEVELOPER.md](./DEVELOPER.md)

## 🗄️ 数据库架构

### 主要表结构

- **users** - 用户表
  - 存储用户账户信息
  - JWT 认证

- **monitoring_tasks** - 监控任务表
  - 用户创建的监控任务
  - 状态：active, paused, completed, cancelled, failed

- **notification_history** - 通知历史表
  - 记录所有发送的通知
  - 包含可用性数据

- **notification_settings** - 通知配置表
  - 用户通知偏好设置
  - Email, Pushover 等配置

- **favorite_campgrounds** - 收藏营地表
  - 用户收藏的营地

详细设计请查看 [DESIGN.md](./DESIGN.md)

## 🔐 安全性

- **密码安全**: bcrypt 哈希
- **认证**: JWT Token (30分钟有效期)
- **授权**: 基于用户的资源隔离
- **SQL 注入防护**: SQLAlchemy ORM 参数化查询
- **环境变量**: 敏感信息存储在 `.env`

## 📊 系统架构

```
┌──────────┐
│  用户    │
└────┬─────┘
     │ HTTP/REST
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

## 🛠️ 开发工具

### 代码格式化

```bash
# 安装工具
pip install black isort

# 格式化代码
black app/
isort app/
```

### 数据库迁移

```bash
# 创建新迁移
./campsite-env/bin/alembic revision --autogenerate -m "Description"

# 应用迁移
./campsite-env/bin/alembic upgrade head

# 回滚
./campsite-env/bin/alembic downgrade -1
```

### 测试

```bash
# 安装 pytest
pip install pytest

# 运行测试
pytest tests/
```

## 📚 完整文档

| 文档 | 描述 |
|------|------|
| [SETUP_INSTRUCTIONS.md](../SETUP_INSTRUCTIONS.md) | 详细安装指南 |
| [API_USAGE.md](./API_USAGE.md) | API 端点说明和使用示例 |
| [DEVELOPER.md](./DEVELOPER.md) | 开发者指南（调试、数据库、队列监控） |
| [DESIGN.md](./DESIGN.md) | 系统设计文档（架构、数据流程、扩展性） |

## 🐛 问题排查

### PostgreSQL 连接失败
```bash
brew services restart postgresql@15
psql campsite_db -c "SELECT version();"
```

### Redis 连接失败
```bash
brew services restart redis
redis-cli ping
```

### RQ Worker 崩溃
```bash
# 确保使用环境变量
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

### 端口被占用
```bash
lsof -ti:8000 | xargs kill -9
```

更多问题请查看 [DEVELOPER.md - 常见问题](./DEVELOPER.md#常见问题)

## 🔮 未来计划

### Phase 2
- [ ] Email 通知支持
- [ ] Pushover 通知支持
- [ ] 定时调度（每小时自动检查）

### Phase 3
- [ ] React 前端管理界面
- [ ] WebSocket 实时通知
- [ ] 营地收藏功能

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

**开始使用**:
1. 运行 `./setup_services.sh` 安装
2. 运行 `./start_services.sh` 启动
3. 访问 http://localhost:8000/docs 查看 API 文档
4. 阅读 [API_USAGE.md](./API_USAGE.md) 学习使用
