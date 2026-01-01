# Campsite Monitoring API 使用指南

## 快速开始

### 1. 启动服务

```bash
cd backend
./start_services.sh
```

这会自动启动：
- PostgreSQL 数据库
- Redis 缓存/队列
- FastAPI API 服务器 (端口 8000)
- RQ Worker 后台任务处理器

### 2. API 文档

访问 http://localhost:8000/docs 查看交互式 API 文档

## API 端点

### 认证 (Authentication)

#### 注册用户
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your_password"}'
```

#### 登录获取 Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "your_password"}'
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer"
}
```

**重要**: 保存返回的 `access_token`，所有后续请求都需要在 Header 中携带：
```
Authorization: Bearer <access_token>
```

#### 获取当前用户信息
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <your_token>"
```

---

### 监控任务 (Monitoring Tasks)

#### 创建监控任务
自动创建后台任务，定期检查营地可用性。

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

参数说明：
- `provider`: 供应商名称 (如 "RecreationDotGov", "ReserveCalifornia")
- `campground_id`: 营地ID
- `campground_name`: 营地名称
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)
- `nights`: (可选) 指定连续夜数进行范围搜索
- `search_mode`: "exact" (精确日期) 或 "range" (范围搜索)

响应：
```json
{
  "id": 1,
  "user_id": 1,
  "provider": "RecreationDotGov",
  "campground_id": "232448",
  "campground_name": "Upper Pines Campground",
  "start_date": "2026-07-01",
  "end_date": "2026-07-05",
  "status": "active",
  "rq_job_id": "abc123...",
  "created_at": "2025-12-31T10:00:00",
  ...
}
```

#### 获取所有监控任务
```bash
curl http://localhost:8000/monitoring/tasks \
  -H "Authorization: Bearer <your_token>"
```

可选查询参数：
- `status`: 按状态筛选 (active, paused, completed, cancelled, failed)

```bash
# 只获取活跃任务
curl http://localhost:8000/monitoring/tasks?status=active \
  -H "Authorization: Bearer <your_token>"
```

#### 获取单个监控任务
```bash
curl http://localhost:8000/monitoring/tasks/1 \
  -H "Authorization: Bearer <your_token>"
```

#### 更新监控任务状态
```bash
# 暂停任务
curl -X PATCH http://localhost:8000/monitoring/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{"status": "paused"}'

# 恢复任务
curl -X PATCH http://localhost:8000/monitoring/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{"status": "active"}'

# 取消任务
curl -X PATCH http://localhost:8000/monitoring/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{"status": "cancelled"}'
```

#### 删除监控任务
```bash
curl -X DELETE http://localhost:8000/monitoring/tasks/1 \
  -H "Authorization: Bearer <your_token>"
```

#### 获取任务的后台作业状态
```bash
curl http://localhost:8000/monitoring/tasks/1/status \
  -H "Authorization: Bearer <your_token>"
```

响应：
```json
{
  "id": "abc123...",
  "status": "finished",
  "result": {
    "status": "success",
    "available": false,
    "message": "No availability yet, will check again"
  },
  "created_at": "2025-12-31T10:00:00",
  "started_at": "2025-12-31T10:00:01",
  "ended_at": "2025-12-31T10:00:02"
}
```

#### 获取通知历史
查看所有发送的通知（当营地变为可用时）。

```bash
curl http://localhost:8000/monitoring/notifications \
  -H "Authorization: Bearer <your_token>"
```

---

### 原有功能 - 即时搜索

原有的即时搜索功能仍然可用（无需认证）：

#### 获取供应商列表
```bash
curl http://localhost:8000/api/providers
```

#### 搜索营地
```bash
curl "http://localhost:8000/api/campgrounds?provider=RecreationDotGov&search=Yosemite"
```

#### 检查可用性
```bash
curl -X POST http://localhost:8000/api/availability \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "RecreationDotGov",
    "campground_id": "232448",
    "start_date": "2026-07-01",
    "end_date": "2026-07-05"
  }'
```

#### 多营地搜索
```bash
curl -X POST http://localhost:8000/api/availability/search \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "RecreationDotGov",
    "campground_name": "Yosemite",
    "start_date": "2026-07-01",
    "end_date": "2026-07-05",
    "search_mode": "exact"
  }'
```

---

## 工作流程示例

### 场景：监控 Yosemite 营地

1. **注册/登录**
```bash
# 注册
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "me@example.com", "password": "mypass123"}'

# 登录获取 token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "me@example.com", "password": "mypass123"}' \
  | jq -r '.access_token')
```

2. **创建监控任务**
```bash
curl -X POST http://localhost:8000/monitoring/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "provider": "RecreationDotGov",
    "campground_id": "232448",
    "campground_name": "Upper Pines Campground",
    "start_date": "2026-07-15",
    "end_date": "2026-07-20",
    "search_mode": "exact"
  }'
```

3. **查看任务状态**
```bash
# 获取所有任务
curl http://localhost:8000/monitoring/tasks \
  -H "Authorization: Bearer $TOKEN"

# 查看后台作业状态
curl http://localhost:8000/monitoring/tasks/1/status \
  -H "Authorization: Bearer $TOKEN"
```

4. **检查通知**
```bash
curl http://localhost:8000/monitoring/notifications \
  -H "Authorization: Bearer $TOKEN"
```

---

## 系统架构

```
┌─────────────┐
│   用户请求   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │ ──► PostgreSQL (用户、任务、通知)
│  API 服务器  │
└──────┬──────┘
       │ 创建任务
       ▼
┌─────────────┐
│    Redis    │ ◄── 队列
│  消息队列   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ RQ Worker   │ ──► 执行检查任务
│ 后台任务处理 │     调用 Camply
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 发现可用性   │ ──► 创建通知记录
│ 发送通知     │
└─────────────┘
```

---

## 数据库状态

### 任务状态 (status)
- `active`: 活跃监控中
- `paused`: 已暂停
- `completed`: 已完成（找到可用性）
- `cancelled`: 用户取消
- `failed`: 执行失败

---

## 故障排查

### 检查服务状态
```bash
# PostgreSQL
brew services list | grep postgresql

# Redis
brew services list | grep redis
redis-cli ping  # 应返回 PONG

# API 服务器
curl http://localhost:8000/health

# 查看日志
tail -f logs/api_server.log
tail -f logs/rq_worker.log
```

### 重启服务
```bash
./stop_services.sh
./start_services.sh
```

### 常见问题

1. **端口占用**
```bash
lsof -ti:8000 | xargs kill -9
```

2. **数据库连接失败**
```bash
brew services restart postgresql@15
```

3. **Redis 连接失败**
```bash
brew services restart redis
```

4. **RQ Worker 不工作**
检查 logs/rq_worker.log，确保使用了 OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

---

## 下一步开发

- [ ] 添加 Email 通知支持
- [ ] 添加 Pushover 通知支持
- [ ] 添加定时调度（每小时检查一次等）
- [ ] 前端监控任务管理界面
- [ ] WebSocket 实时通知
- [ ] 营地收藏功能
