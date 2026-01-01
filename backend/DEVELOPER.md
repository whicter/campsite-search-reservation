# Developer Documentation - 开发者文档

## 目录
- [开发环境设置](#开发环境设置)
- [项目结构](#项目结构)
- [开发工作流](#开发工作流)
- [数据库操作](#数据库操作)
- [Redis与队列监控](#redis与队列监控)
- [调试技巧](#调试技巧)
- [测试指南](#测试指南)
- [常见问题](#常见问题)

---

## 开发环境设置

### 必需软件
- Python 3.12+
- PostgreSQL 15
- Redis
- Homebrew (macOS)

### 首次设置

```bash
# 1. 克隆项目
cd /path/to/campsite-search-resevation/backend

# 2. 创建虚拟环境
python3 -m venv campsite-env

# 3. 激活虚拟环境
source campsite-env/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 安装并启动服务
./setup_services.sh

# 6. 运行数据库迁移（已在setup中完成）
./campsite-env/bin/alembic upgrade head
```

### 环境变量配置

编辑 `.env` 文件：
```bash
# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3002

# Database
DATABASE_URL=postgresql://localhost/campsite_db
REDIS_URL=redis://localhost:6379/0

# JWT Authentication
SECRET_KEY=your-secret-key-here  # 已自动生成
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email notifications (可选)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 应用入口
│   ├── database.py                # 数据库连接配置
│   ├── db_models.py               # SQLAlchemy ORM 模型
│   ├── models.py                  # Pydantic 模型（原有）
│   ├── api_models.py              # Pydantic API 模型（新）
│   ├── auth.py                    # JWT 认证逻辑
│   ├── redis_client.py            # Redis 连接
│   ├── tasks.py                   # RQ 后台任务
│   ├── scheduler.py               # 任务调度器
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                # Provider 基类
│   │   ├── camply_provider.py     # Camply 集成
│   │   └── sanmateo_provider.py   # 示例 provider
│   └── routers/
│       ├── __init__.py
│       ├── auth.py                # 认证路由
│       └── monitoring.py          # 监控任务路由
│
├── alembic/
│   ├── versions/                  # 数据库迁移文件
│   └── env.py                     # Alembic 配置
│
├── logs/                          # 日志目录
│   ├── api_server.log
│   └── rq_worker.log
│
├── .env                           # 环境变量
├── alembic.ini                    # Alembic 配置
├── requirements.txt               # Python 依赖
├── database_schema.sql            # 数据库 schema
├── setup_services.sh              # 服务安装脚本
├── start_services.sh              # 服务启动脚本
├── stop_services.sh               # 服务停止脚本
├── DESIGN.md                      # 系统设计文档
├── DEVELOPER.md                   # 本文档
└── API_USAGE.md                   # API 使用文档
```

### 核心模块说明

#### 1. `app/main.py`
FastAPI 应用主入口，定义所有路由和中间件。

```python
from fastapi import FastAPI
from .routers import auth, monitoring

app = FastAPI(title="Campsite Search API")
app.include_router(auth.router)
app.include_router(monitoring.router)
```

#### 2. `app/database.py`
数据库连接池和会话管理。

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """FastAPI 依赖注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### 3. `app/db_models.py`
SQLAlchemy ORM 模型定义。

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    # ...
```

#### 4. `app/auth.py`
JWT 认证和密码哈希。

```python
def get_current_user(credentials, db):
    """验证 JWT token，返回当前用户"""
    # ...
```

#### 5. `app/tasks.py`
RQ 后台任务定义。

```python
def check_campsite_availability(task_id: int):
    """检查营地可用性的后台任务"""
    # ...
```

---

## 开发工作流

### 启动开发服务器

**方式1: 使用启动脚本（推荐）**
```bash
./start_services.sh
```

**方式2: 手动启动**
```bash
# Terminal 1: API Server
./campsite-env/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: RQ Worker
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES \
  ./campsite-env/bin/rq worker monitoring --url redis://localhost:6379/0

# Terminal 3: (可选) 前端
cd ../frontend
yarn start
```

### 查看日志

```bash
# API Server 日志
tail -f logs/api_server.log

# RQ Worker 日志
tail -f logs/rq_worker.log

# 实时查看（彩色输出）
./campsite-env/bin/uvicorn app.main:app --reload --log-level debug
```

### 停止服务

```bash
./stop_services.sh
```

---

## 数据库操作

### 1. 查看所有表

```bash
psql campsite_db -c "\dt"
```

输出示例：
```
               List of relations
 Schema |         Name          | Type  | Owner
--------+-----------------------+-------+-------
 public | alembic_version       | table | cohan
 public | favorite_campgrounds  | table | cohan
 public | monitoring_tasks      | table | cohan
 public | notification_history  | table | cohan
 public | notification_settings | table | cohan
 public | users                 | table | cohan
```

### 2. 查看表结构

```bash
# 查看 users 表结构
psql campsite_db -c "\d users"

# 查看 monitoring_tasks 表结构
psql campsite_db -c "\d monitoring_tasks"
```

### 3. 查询数据

**查看所有用户**
```bash
psql campsite_db -c "SELECT id, email, created_at FROM users;"
```

**查看所有监控任务**
```bash
psql campsite_db -c "
  SELECT id, user_id, campground_name, status, created_at
  FROM monitoring_tasks
  ORDER BY created_at DESC
  LIMIT 10;
"
```

**查看活跃任务**
```bash
psql campsite_db -c "
  SELECT id, campground_name, status, last_checked_at
  FROM monitoring_tasks
  WHERE status = 'active';
"
```

**查看通知历史**
```bash
psql campsite_db -c "
  SELECT id, campground_name, sent_at, success
  FROM notification_history
  ORDER BY sent_at DESC
  LIMIT 10;
"
```

### 4. 进入交互式 SQL 终端

```bash
psql campsite_db
```

常用 psql 命令：
```sql
-- 列出所有表
\dt

-- 查看表结构
\d table_name

-- 查看索引
\di

-- 退出
\q

-- 执行 SQL
SELECT * FROM users;

-- 美化输出
\x
SELECT * FROM monitoring_tasks LIMIT 1;
```

### 5. 数据库迁移

#### 创建新迁移

```bash
# 修改 app/db_models.py 后，生成迁移文件
./campsite-env/bin/alembic revision --autogenerate -m "Add new column"
```

#### 查看迁移历史

```bash
./campsite-env/bin/alembic history
```

#### 应用迁移

```bash
# 升级到最新版本
./campsite-env/bin/alembic upgrade head

# 升级到特定版本
./campsite-env/bin/alembic upgrade <revision>

# 降级一个版本
./campsite-env/bin/alembic downgrade -1
```

#### 查看当前版本

```bash
./campsite-env/bin/alembic current
```

### 6. 数据库备份与恢复

**备份**
```bash
# 备份整个数据库
pg_dump campsite_db > backup_$(date +%Y%m%d).sql

# 只备份数据（不含 schema）
pg_dump --data-only campsite_db > data_backup.sql

# 只备份 schema
pg_dump --schema-only campsite_db > schema_backup.sql
```

**恢复**
```bash
# 恢复数据库
psql campsite_db < backup_20251231.sql
```

**重置数据库**
```bash
# 删除所有表
psql campsite_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# 重新运行迁移
./campsite-env/bin/alembic upgrade head
```

---

## Redis与队列监控

### 1. Redis 基本操作

#### 连接 Redis
```bash
redis-cli
```

#### 常用 Redis 命令

```bash
# 测试连接
redis-cli ping
# 输出: PONG

# 查看所有键
redis-cli KEYS '*'

# 查看 RQ 队列
redis-cli KEYS 'rq:*'

# 查看队列长度
redis-cli LLEN rq:queue:monitoring

# 查看正在运行的 worker
redis-cli SMEMBERS rq:workers

# 查看失败的任务
redis-cli ZRANGE rq:failed:monitoring 0 -1

# 清空所有数据（谨慎使用！）
redis-cli FLUSHALL
```

### 2. RQ 队列监控

#### 使用 RQ CLI

```bash
# 查看队列状态
./campsite-env/bin/rq info --url redis://localhost:6379/0

# 查看所有队列
./campsite-env/bin/rq info --url redis://localhost:6379/0 --all

# 清空队列
./campsite-env/bin/rq empty monitoring --url redis://localhost:6379/0

# 查看失败任务
./campsite-env/bin/rq info --url redis://localhost:6379/0 failed
```

输出示例：
```
monitoring      |██████████ 0
0 queues, 0 jobs total

0 workers, monitoring
```

#### 安装 RQ Dashboard (可选)

```bash
# 安装
./campsite-env/bin/pip install rq-dashboard

# 启动 Dashboard
./campsite-env/bin/rq-dashboard --redis-url redis://localhost:6379/0

# 访问 http://localhost:9181
```

RQ Dashboard 功能：
- 查看所有队列状态
- 查看 worker 状态
- 查看任务详情
- 重试失败任务
- 删除任务

### 3. 监控任务执行

#### 查看任务日志

```bash
# 实时查看 worker 日志
tail -f logs/rq_worker.log
```

日志示例：
```
16:03:31 monitoring: app.tasks.check_campsite_availability(task_id=2)
✅ Loaded 15 camply providers
16:03:32 Successfully completed app.tasks.check_campsite_availability(task_id=2)
16:03:32 monitoring: Job OK (bcd2ce65-7396-43a6-a59d-242fe419f56b)
```

#### Python 脚本监控

创建 `scripts/monitor_queue.py`:
```python
from redis import Redis
from rq import Queue
from rq.job import Job

redis_conn = Redis.from_url('redis://localhost:6379/0')
queue = Queue('monitoring', connection=redis_conn)

print(f"队列长度: {len(queue)}")
print(f"活跃 worker: {queue.worker_count()}")

# 查看所有任务
for job_id in queue.job_ids:
    job = Job.fetch(job_id, connection=redis_conn)
    print(f"任务 {job.id}: {job.get_status()}")
```

运行：
```bash
./campsite-env/bin/python scripts/monitor_queue.py
```

### 4. 任务管理 Python API

#### 获取任务状态

```python
from redis import Redis
from rq.job import Job

redis_conn = Redis.from_url('redis://localhost:6379/0')

# 获取任务
job = Job.fetch('job-id-here', connection=redis_conn)

print(f"状态: {job.get_status()}")
print(f"结果: {job.result}")
print(f"创建时间: {job.created_at}")
print(f"开始时间: {job.started_at}")
print(f"结束时间: {job.ended_at}")
```

#### 取消任务

```python
job.cancel()
```

#### 重新执行失败任务

```python
from rq import Queue
from rq.registry import FailedJobRegistry

queue = Queue('monitoring', connection=redis_conn)
failed_registry = FailedJobRegistry(queue=queue)

# 获取所有失败任务
for job_id in failed_registry.get_job_ids():
    job = Job.fetch(job_id, connection=redis_conn)

    # 重新入队
    failed_registry.requeue(job_id)
    print(f"重新入队: {job_id}")
```

---

## 调试技巧

### 1. API 调试

#### 使用 FastAPI Swagger UI
访问 http://localhost:8000/docs 使用交互式 API 文档。

#### 使用 curl 调试

```bash
# 设置变量
API_URL="http://localhost:8000"

# 注册用户
curl -X POST $API_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}' | jq

# 登录获取 token
TOKEN=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 创建监控任务
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
```

#### Python 调试脚本

创建 `scripts/test_api.py`:
```python
import requests

API_URL = "http://localhost:8000"

# 注册
response = requests.post(
    f"{API_URL}/auth/register",
    json={"email": "test@example.com", "password": "test123"}
)
print("注册:", response.json())

# 登录
response = requests.post(
    f"{API_URL}/auth/login",
    json={"email": "test@example.com", "password": "test123"}
)
token = response.json()["access_token"]
print("Token:", token[:50])

# 创建任务
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{API_URL}/monitoring/tasks",
    headers=headers,
    json={
        "provider": "RecreationDotGov",
        "campground_id": "232448",
        "campground_name": "Test",
        "start_date": "2026-07-01",
        "end_date": "2026-07-05",
        "search_mode": "exact"
    }
)
print("任务:", response.json())
```

### 2. 数据库调试

#### 使用 SQLAlchemy Echo

在 `app/database.py` 中启用日志：
```python
engine = create_engine(DATABASE_URL, echo=True)  # 打印所有 SQL
```

#### 直接执行 SQL

```python
from app.database import SessionLocal

db = SessionLocal()
result = db.execute("SELECT * FROM users LIMIT 5")
for row in result:
    print(row)
db.close()
```

### 3. 后台任务调试

#### 同步执行任务（不使用队列）

在开发时可以直接调用任务函数：
```python
from app.tasks import check_campsite_availability

# 直接执行，不入队
result = check_campsite_availability(task_id=1)
print(result)
```

#### 添加日志

在 `app/tasks.py` 中：
```python
import logging

logger = logging.getLogger(__name__)

def check_campsite_availability(task_id: int):
    logger.info(f"开始检查任务 {task_id}")
    # ...
    logger.info(f"任务 {task_id} 完成")
```

### 4. VS Code 调试配置

创建 `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "RQ Worker",
      "type": "python",
      "request": "launch",
      "module": "rq.cli",
      "args": [
        "worker",
        "monitoring",
        "--url",
        "redis://localhost:6379/0"
      ],
      "env": {
        "OBJC_DISABLE_INITIALIZE_FORK_SAFETY": "YES"
      }
    }
  ]
}
```

---

## 测试指南

### 单元测试

创建 `tests/test_auth.py`:
```python
import pytest
from app.auth import get_password_hash, verify_password

def test_password_hashing():
    password = "test123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)
```

### API 测试

创建 `tests/test_api.py`:
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register():
    response = client.post(
        "/auth/register",
        json={"email": "test@test.com", "password": "test123"}
    )
    assert response.status_code == 201
    assert "id" in response.json()

def test_login():
    # 先注册
    client.post(
        "/auth/register",
        json={"email": "login@test.com", "password": "test123"}
    )

    # 登录
    response = client.post(
        "/auth/login",
        json={"email": "login@test.com", "password": "test123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

运行测试：
```bash
./campsite-env/bin/pytest tests/
```

---

## 常见问题

### 1. 端口被占用

**问题**: `Address already in use`

**解决**:
```bash
# 查找占用端口的进程
lsof -ti:8000

# 杀死进程
lsof -ti:8000 | xargs kill -9

# 或使用脚本
./stop_services.sh
```

### 2. PostgreSQL 连接失败

**问题**: `FATAL: role "postgres" does not exist`

**解决**:
```bash
# 重启 PostgreSQL
brew services restart postgresql@15

# 检查服务状态
brew services list | grep postgresql
```

### 3. Redis 连接失败

**问题**: `Error 61 connecting to localhost:6379. Connection refused.`

**解决**:
```bash
# 启动 Redis
brew services start redis

# 测试连接
redis-cli ping
```

### 4. RQ Worker 崩溃

**问题**: `objc[xxxxx]: +[NSMutableString initialize] may have been in progress`

**解决**:
```bash
# 设置环境变量
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# 或在启动命令前添加
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES rq worker monitoring
```

### 5. Alembic 迁移冲突

**问题**: `Target database is not up to date`

**解决**:
```bash
# 查看当前版本
./campsite-env/bin/alembic current

# 查看历史
./campsite-env/bin/alembic history

# 降级然后升级
./campsite-env/bin/alembic downgrade base
./campsite-env/bin/alembic upgrade head
```

### 6. JWT Token 过期

**问题**: `Could not validate credentials`

**解决**: 重新登录获取新 token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123"}'
```

### 7. 依赖版本冲突

**问题**: `ERROR: Cannot install package due to conflict`

**解决**:
```bash
# 删除虚拟环境
rm -rf campsite-env

# 重新创建
python3 -m venv campsite-env
source campsite-env/bin/activate
pip install -r requirements.txt
```

---

## 性能分析

### 1. API 性能分析

```bash
# 使用 ab (Apache Bench)
ab -n 100 -c 10 http://localhost:8000/

# 使用 wrk
wrk -t2 -c10 -d30s http://localhost:8000/
```

### 2. 数据库查询分析

```sql
-- PostgreSQL 查询分析
EXPLAIN ANALYZE SELECT * FROM monitoring_tasks WHERE user_id = 1;

-- 查看慢查询
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

### 3. Python 性能分析

```python
import cProfile
import pstats

# 分析函数
profiler = cProfile.Profile()
profiler.enable()

# 你的代码
check_campsite_availability(1)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

---

## 最佳实践

### 1. 代码风格
- 遵循 PEP 8
- 使用 black 格式化: `black app/`
- 使用 isort 排序导入: `isort app/`

### 2. Git 提交
```bash
# 好的提交信息
git commit -m "feat: add email notification support"
git commit -m "fix: handle timeout in camply provider"
git commit -m "docs: update API usage guide"
```

### 3. 环境隔离
- 开发: `DATABASE_URL=postgresql://localhost/campsite_db_dev`
- 测试: `DATABASE_URL=postgresql://localhost/campsite_db_test`
- 生产: 使用环境变量

### 4. 日志记录
```python
import logging

logger = logging.getLogger(__name__)

# 使用不同级别
logger.debug("详细调试信息")
logger.info("一般信息")
logger.warning("警告")
logger.error("错误")
logger.critical("严重错误")
```

---

## 资源链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [RQ 文档](https://python-rq.org/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Redis 文档](https://redis.io/documentation)

---

## 获取帮助

遇到问题？
1. 查看日志文件
2. 检查数据库连接
3. 验证 Redis 服务
4. 查阅本文档
5. 查看 API 文档 (http://localhost:8000/docs)
