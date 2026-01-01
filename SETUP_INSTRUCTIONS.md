# Setup Instructions - 安装指南

## 快速开始（推荐）

### 一键安装所有服务

```bash
cd backend
./setup_services.sh
```

这个脚本会自动：
- 检查并安装 PostgreSQL@15
- 检查并安装 Redis
- 启动服务
- 创建数据库 `campsite_db`
- 生成 SECRET_KEY
- 创建 `.env` 配置文件

---

## 手动安装（如需要）

### 1. 安装PostgreSQL

```bash
# macOS
brew install postgresql@15

# 启动PostgreSQL服务
brew services start postgresql@15

# 创建数据库
createdb campsite_db

# 验证
psql campsite_db
# 然后输入 \q 退出
```

### 2. 安装Redis

```bash
# macOS
brew install redis

# 启动Redis服务
brew services start redis

# 验证
redis-cli ping
# 应该返回 PONG
```

### 3. 配置数据库连接

创建 `backend/.env` 文件（如果还没有）并添加：

```bash
# 现有配置
CORS_ORIGINS=http://localhost:3000,http://localhost:3002

# 新增数据库配置
DATABASE_URL=postgresql://localhost/campsite_db
REDIS_URL=redis://localhost:6379/0

# JWT密钥（用于用户认证）
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. 初始化数据库

```bash
cd backend

# 安装依赖
./campsite-env/bin/pip install -r requirements.txt

# 运行迁移（创建表）
# Alembic 已经初始化好了
./campsite-env/bin/alembic upgrade head
```

---

## 启动和停止服务

### 启动所有服务（推荐）

```bash
cd backend
./start_services.sh
```

这会启动：
- PostgreSQL（如果未运行）
- Redis（如果未运行）
- FastAPI 服务器（端口 8000）
- RQ Worker（后台任务处理器）

### 停止所有服务

```bash
cd backend
./stop_services.sh
```

### 手动启动（如需要）

需要在3个终端窗口中分别运行：

#### Terminal 1: FastAPI Backend
```bash
cd backend
./campsite-env/bin/uvicorn app.main:app --reload
```

#### Terminal 2: RQ Worker
```bash
cd backend
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES \
  ./campsite-env/bin/rq worker monitoring --url redis://localhost:6379/0
```

#### Terminal 3: Frontend (React，可选)
```bash
cd frontend
yarn start
```

## 可选：RQ Dashboard（查看任务队列）

```bash
# 安装
./campsite-env/bin/pip install rq-dashboard

# 运行
./campsite-env/bin/rq-dashboard --redis-url redis://localhost:6379/0

# 访问 http://localhost:9181
```

## 验证安装

### 测试PostgreSQL连接
```bash
psql campsite_db -c "SELECT version();"
```

### 测试Redis连接
```bash
redis-cli ping
```

### 测试Python依赖
```bash
cd backend
./campsite-env/bin/python -c "import sqlalchemy, redis, rq; print('All dependencies OK')"
```

## 常见问题

### PostgreSQL连接错误
```bash
# 确保服务运行
brew services list | grep postgresql

# 重启服务
brew services restart postgresql@15
```

### Redis连接错误
```bash
# 确保服务运行
brew services list | grep redis

# 重启服务
brew services restart redis
```

### 端口冲突
- PostgreSQL默认端口：5432
- Redis默认端口：6379
- FastAPI默认端口：8000
- React默认端口：3000/3002
- RQ Dashboard默认端口：9181

---

## 访问服务

安装和启动完成后，可以访问：

- **API 服务**: http://localhost:8000
- **API 文档（Swagger）**: http://localhost:8000/docs
- **RQ Dashboard（如已安装）**: http://localhost:9181

---

## 下一步

1. **查看 API 使用文档**: `backend/API_USAGE.md`
2. **查看开发者文档**: `backend/DEVELOPER.md`
3. **查看系统设计文档**: `backend/DESIGN.md`

---

## 完整文档索引

- **SETUP_INSTRUCTIONS.md** (本文档) - 安装指南
- **API_USAGE.md** - API 使用文档，包含所有端点说明和示例
- **DEVELOPER.md** - 开发者文档，包含开发工作流、调试、数据库操作等
- **DESIGN.md** - 系统设计文档，包含架构、数据流程、数据库设计等
