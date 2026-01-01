# Quick Reference - 快速参考

## 🚀 常用命令

### 服务管理

```bash
# 安装所有服务（首次）
./setup_services.sh

# 启动所有服务
./start_services.sh

# 停止所有服务
./stop_services.sh
```

### 数据库查询

```bash
# 连接数据库
psql campsite_db

# 查看所有表
psql campsite_db -c "\dt"

# 查看用户
psql campsite_db -c "SELECT id, email, created_at FROM users;"

# 查看活跃任务
psql campsite_db -c "SELECT id, campground_name, status FROM monitoring_tasks WHERE status='active';"

# 查看通知历史
psql campsite_db -c "SELECT id, campground_name, sent_at FROM notification_history ORDER BY sent_at DESC LIMIT 10;"
```

### Redis 和队列

```bash
# 测试 Redis 连接
redis-cli ping

# 查看队列长度
redis-cli LLEN rq:queue:monitoring

# 查看所有 RQ 相关键
redis-cli KEYS 'rq:*'

# RQ 队列信息
./campsite-env/bin/rq info --url redis://localhost:6379/0

# RQ Dashboard
./campsite-env/bin/rq-dashboard --redis-url redis://localhost:6379/0
# 访问 http://localhost:9181
```

### 日志查看

```bash
# API 服务器日志
tail -f logs/api_server.log

# RQ Worker 日志
tail -f logs/rq_worker.log

# 实时日志（彩色输出）
./campsite-env/bin/uvicorn app.main:app --reload --log-level debug
```

### 数据库迁移

```bash
# 查看当前版本
./campsite-env/bin/alembic current

# 查看迁移历史
./campsite-env/bin/alembic history

# 创建新迁移
./campsite-env/bin/alembic revision --autogenerate -m "描述"

# 应用迁移
./campsite-env/bin/alembic upgrade head

# 回滚
./campsite-env/bin/alembic downgrade -1
```

## 🔑 API 快速测试

### 用户认证

```bash
# 设置 API URL
API_URL="http://localhost:8000"

# 注册
curl -X POST $API_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# 登录
TOKEN=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}' \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "Token: $TOKEN"

# 获取用户信息
curl -s $API_URL/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 监控任务

```bash
# 创建任务
curl -X POST $API_URL/monitoring/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "provider":"RecreationDotGov",
    "campground_id":"232448",
    "campground_name":"Test Campground",
    "start_date":"2026-07-01",
    "end_date":"2026-07-05",
    "search_mode":"exact"
  }' | jq

# 获取所有任务
curl -s $API_URL/monitoring/tasks \
  -H "Authorization: Bearer $TOKEN" | jq

# 获取特定任务
curl -s $API_URL/monitoring/tasks/1 \
  -H "Authorization: Bearer $TOKEN" | jq

# 暂停任务
curl -X PATCH $API_URL/monitoring/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status":"paused"}' | jq

# 恢复任务
curl -X PATCH $API_URL/monitoring/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status":"active"}' | jq

# 删除任务
curl -X DELETE $API_URL/monitoring/tasks/1 \
  -H "Authorization: Bearer $TOKEN"

# 查看任务作业状态
curl -s $API_URL/monitoring/tasks/1/status \
  -H "Authorization: Bearer $TOKEN" | jq

# 查看通知历史
curl -s $API_URL/monitoring/notifications \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 即时搜索

```bash
# 获取供应商列表
curl -s $API_URL/api/providers | jq

# 搜索营地
curl -s "$API_URL/api/campgrounds?provider=RecreationDotGov&search=Yosemite" | jq

# 检查可用性
curl -X POST $API_URL/api/availability \
  -H "Content-Type: application/json" \
  -d '{
    "provider":"RecreationDotGov",
    "campground_id":"232448",
    "start_date":"2026-07-01",
    "end_date":"2026-07-05"
  }' | jq
```

## 🐛 故障排查

### 问题：端口被占用

```bash
# 查找进程
lsof -ti:8000

# 杀死进程
lsof -ti:8000 | xargs kill -9

# 或使用停止脚本
./stop_services.sh
```

### 问题：PostgreSQL 连接失败

```bash
# 检查服务状态
brew services list | grep postgresql

# 重启服务
brew services restart postgresql@15

# 测试连接
psql campsite_db -c "SELECT version();"
```

### 问题：Redis 连接失败

```bash
# 检查服务状态
brew services list | grep redis

# 重启服务
brew services restart redis

# 测试连接
redis-cli ping
```

### 问题：RQ Worker 崩溃

```bash
# 设置环境变量
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# 重启 worker
./stop_services.sh
./start_services.sh
```

### 问题：JWT Token 过期

```bash
# 重新登录获取新 token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}' \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
```

### 问题：数据库迁移冲突

```bash
# 查看当前状态
./campsite-env/bin/alembic current

# 重置到初始状态
./campsite-env/bin/alembic downgrade base

# 重新应用所有迁移
./campsite-env/bin/alembic upgrade head
```

## 📊 监控指标

### 系统健康检查

```bash
# API 健康检查
curl http://localhost:8000/health

# PostgreSQL 连接
psql campsite_db -c "SELECT 1;"

# Redis 连接
redis-cli ping

# 检查服务状态
brew services list
```

### 性能指标

```bash
# PostgreSQL 连接数
psql campsite_db -c "SELECT count(*) FROM pg_stat_activity;"

# 数据库大小
psql campsite_db -c "SELECT pg_size_pretty(pg_database_size('campsite_db'));"

# Redis 内存使用
redis-cli INFO memory | grep used_memory_human

# RQ 队列统计
./campsite-env/bin/rq info --url redis://localhost:6379/0
```

### 数据统计

```bash
# 用户数量
psql campsite_db -c "SELECT COUNT(*) FROM users;"

# 活跃任务数量
psql campsite_db -c "SELECT COUNT(*) FROM monitoring_tasks WHERE status='active';"

# 今天的通知数量
psql campsite_db -c "SELECT COUNT(*) FROM notification_history WHERE DATE(sent_at) = CURRENT_DATE;"

# 按状态统计任务
psql campsite_db -c "
  SELECT status, COUNT(*)
  FROM monitoring_tasks
  GROUP BY status
  ORDER BY COUNT(*) DESC;
"
```

## 🔧 常用 SQL 查询

```sql
-- 查看最近创建的任务
SELECT id, user_id, campground_name, status, created_at
FROM monitoring_tasks
ORDER BY created_at DESC
LIMIT 10;

-- 查看用户的所有任务
SELECT id, campground_name, status, created_at
FROM monitoring_tasks
WHERE user_id = 1
ORDER BY created_at DESC;

-- 查看失败的任务
SELECT id, campground_name, error_message, created_at
FROM monitoring_tasks
WHERE status = 'failed';

-- 查看今天的通知
SELECT id, campground_name, sent_at, success
FROM notification_history
WHERE DATE(sent_at) = CURRENT_DATE
ORDER BY sent_at DESC;

-- 查看用户统计
SELECT
  u.id,
  u.email,
  COUNT(mt.id) as task_count,
  COUNT(CASE WHEN mt.status = 'active' THEN 1 END) as active_tasks
FROM users u
LEFT JOIN monitoring_tasks mt ON u.id = mt.user_id
GROUP BY u.id, u.email;
```

## 🔐 环境变量

```bash
# .env 文件关键配置

# 数据库
DATABASE_URL=postgresql://localhost/campsite_db
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3002

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## 📁 重要文件位置

```
backend/
├── .env                          # 环境变量配置
├── logs/
│   ├── api_server.log           # API 日志
│   └── rq_worker.log            # Worker 日志
├── alembic/
│   └── versions/                # 数据库迁移文件
└── database_schema.sql          # 数据库 schema
```

## 🔗 重要 URL

| 服务 | URL |
|------|-----|
| API 根路径 | http://localhost:8000 |
| API 文档 (Swagger) | http://localhost:8000/docs |
| API 文档 (ReDoc) | http://localhost:8000/redoc |
| RQ Dashboard | http://localhost:9181 |

## 📞 获取帮助

1. **查看日志**: `tail -f logs/*.log`
2. **查看文档**: `backend/DEVELOPER.md`
3. **检查服务**: `brew services list`
4. **数据库状态**: `psql campsite_db -c "\conninfo"`
5. **Redis 状态**: `redis-cli INFO`

---

**提示**: 将此文件加入书签，方便快速查找常用命令！
