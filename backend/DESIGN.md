# Campsite Search & Monitoring System - 系统设计文档

## 目录
- [系统概述](#系统概述)
- [架构设计](#架构设计)
- [数据流程](#数据流程)
- [数据库设计](#数据库设计)
- [API设计](#api设计)
- [任务队列设计](#任务队列设计)
- [认证与授权](#认证与授权)
- [扩展性考虑](#扩展性考虑)

---

## 系统概述

### 项目目标
构建一个自动化营地监控系统，用户可以：
1. 即时搜索营地可用性（现有功能）
2. 创建监控任务，自动检查营地可用性
3. 营地可用时接收通知
4. 管理多个监控任务

### 技术栈
- **后端**: FastAPI (Python)
- **数据库**: PostgreSQL 15
- **缓存/队列**: Redis
- **任务队列**: RQ (Redis Queue)
- **认证**: JWT (JSON Web Tokens)
- **ORM**: SQLAlchemy 2.0
- **迁移**: Alembic
- **营地数据**: Camply CLI

---

## 架构设计

### 系统架构图

```
┌──────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                          (React)                             │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI Server                           │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐     │
│  │   Auth     │  │  Instant   │  │  Monitoring Tasks   │     │
│  │  Routes    │  │  Search    │  │      Routes         │     │
│  └────────────┘  └────────────┘  └─────────────────────┘     │
│         │              │                    │                │
│         ▼              ▼                    ▼                │
│  ┌────────────────────────────────────────────────┐          │
│  │          Authentication Middleware             │          │
│  │              (JWT Validation)                  │          │
│  └────────────────────────────────────────────────┘          │
└────────────┬──────────────────────┬──────────────────────────┘
             │                      │
             ▼                      ▼
┌─────────────────────┐   ┌──────────────────────┐
│    PostgreSQL       │   │       Redis          │
│                     │   │                      │
│ ┌─────────────────┐ │   │ ┌────────────────┐   │
│ │ Users           │ │   │ │ RQ Queues      │   │ 
│ │ Monitoring Tasks│ │   │ │ - monitoring   │   │
│ │ Notifications   │ │   │ │ Cache (future) │   │
│ │ Settings        │ │   │ └────────────────┘   │
│ │ Favorites       │ │   │                      │
│ └─────────────────┘ │   └──────────┬───────────┘
└─────────────────────┘              │
                                     │ Job Queue
                                     ▼
                        ┌──────────────────────┐
                        │     RQ Worker        │
                        │                      │
                        │ ┌──────────────────┐ │
                        │ │ Task Execution   │ │
                        │ │ - Check Avail.   │ │
                        │ │ - Send Notify    │ │
                        │ └──────────────────┘ │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   Camply Provider    │
                        │                      │
                        │ - RecreationDotGov   │
                        │ - ReserveCalifornia  │
                        │ - Other providers    │
                        └──────────────────────┘
```

### 组件说明

#### 1. FastAPI Server
- **职责**: 处理 HTTP 请求、业务逻辑、认证授权
- **端口**: 8000
- **进程模型**: 单进程（开发）/ 多进程（生产环境使用 gunicorn）

#### 2. PostgreSQL
- **职责**: 持久化数据存储
- **端口**: 5432
- **数据**: 用户、监控任务、通知、配置

#### 3. Redis
- **职责**:
  - RQ 消息队列（主要用途）
  - 缓存（未来）
  - 会话存储（未来）
- **端口**: 6379

#### 4. RQ Worker
- **职责**: 执行后台任务
- **进程模型**: 单进程或多进程
- **任务**: 检查营地可用性、发送通知

---

## 数据流程

### 流程 1: 用户注册与登录

```
┌─────┐                                     ┌──────────┐
│User │                                     │FastAPI  │
└──┬──┘                                     └────┬─────┘
   │                                             │
   │  POST /auth/register                        │
   │  {email, password}                          │
   ├────────────────────────────────────────────►│
   │                                             │
   │                                             │ Hash password
   │                                             │ (bcrypt)
   │                                             │
   │                                             ▼
   │                                        ┌─────────┐
   │                                        │PostgreSQL│
   │                                        └────┬────┘
   │                                             │
   │                                             │ INSERT user
   │                                             │
   │  {id, email, created_at}                   │
   │◄────────────────────────────────────────────┤
   │                                             │
   │  POST /auth/login                           │
   │  {email, password}                          │
   ├────────────────────────────────────────────►│
   │                                             │
   │                                             │ Verify password
   │                                             │ Generate JWT
   │                                             │
   │  {access_token, token_type}                │
   │◄────────────────────────────────────────────┤
   │                                             │
```

**步骤说明**:
1. 用户提交邮箱和密码
2. FastAPI 使用 bcrypt 哈希密码
3. 存储用户信息到 PostgreSQL
4. 登录时验证密码
5. 生成 JWT token (包含用户邮箱和过期时间)
6. 返回 token 给客户端

### 流程 2: 创建监控任务

```
┌─────┐         ┌────────┐         ┌──────────┐         ┌─────┐
│User │         │FastAPI │         │PostgreSQL│         │Redis│
└──┬──┘         └───┬────┘         └────┬─────┘         └──┬──┘
   │                │                   │                   │
   │ POST /monitoring/tasks             │                   │
   │ + JWT Token                        │                   │
   ├───────────────►│                   │                   │
   │                │                   │                   │
   │                │ Verify JWT        │                   │
   │                │ Extract user_id   │                   │
   │                │                   │                   │
   │                │ INSERT task       │                   │
   │                ├──────────────────►│                   │
   │                │                   │                   │
   │                │ task created      │                   │
   │                │◄──────────────────┤                   │
   │                │                   │                   │
   │                │ ENQUEUE job to RQ │                   │
   │                ├───────────────────┴──────────────────►│
   │                │                   │                   │
   │                │ UPDATE task.rq_job_id                 │
   │                ├──────────────────►│                   │
   │                │                   │                   │
   │ task response  │                   │                   │
   │◄───────────────┤                   │                   │
   │                │                   │                   │
```

**步骤说明**:
1. 用户发送创建任务请求，携带 JWT token
2. FastAPI 验证 token，提取 user_id
3. 创建 `MonitoringTask` 记录（status=active）
4. 将任务 ID 加入 RQ 队列
5. 更新任务记录，保存 RQ job_id
6. 返回任务信息给用户

### 流程 3: 后台任务执行

```
┌─────────┐    ┌────────┐    ┌──────────┐    ┌──────┐    ┌──────────┐
│RQ Worker│    │Redis   │    │PostgreSQL│    │Camply│    │Notification│
└────┬────┘    └───┬────┘    └────┬─────┘    └──┬───┘    └─────┬────┘
     │             │              │              │              │
     │ DEQUEUE job │              │              │              │
     │◄────────────┤              │              │              │
     │             │              │              │              │
     │ GET task    │              │              │              │
     ├─────────────┴─────────────►│              │              │
     │             │              │              │              │
     │ task data   │              │              │              │
     │◄────────────┴──────────────┤              │              │
     │             │              │              │              │
     │ UPDATE last_checked_at     │              │              │
     ├─────────────┴─────────────►│              │              │
     │             │              │              │              │
     │ Check availability          │              │              │
     ├─────────────┴──────────────┴─────────────►│              │
     │             │              │              │              │
     │             │              │   API call   │              │
     │             │              │   to provider│              │
     │             │              │              │              │
     │             │              │  result      │              │
     │◄────────────┴──────────────┴──────────────┤              │
     │             │              │              │              │
     │             │              │              │              │
     │ IF available:              │              │              │
     │   - UPDATE status=completed│              │              │
     │   - INSERT notification    │              │              │
     ├─────────────┴─────────────►│              │              │
     │             │              ├──────────────┴──────────────►│
     │             │              │              │              │
     │ ELSE:                      │              │              │
     │   - Continue monitoring    │              │              │
     │   - Re-enqueue (future)    │              │              │
     │             │              │              │              │
```

**步骤说明**:
1. RQ Worker 从 Redis 队列获取任务
2. 从数据库读取任务详情
3. 更新 `last_checked_at` 时间戳
4. 调用 Camply Provider 检查可用性
5. 如果可用：
   - 更新任务状态为 `completed`
   - 创建通知记录
   - 发送通知（Email/Pushover - 未来实现）
6. 如果不可用：
   - 任务继续保持 `active` 状态
   - 等待下次调度（未来实现定时重试）

### 流程 4: 查询任务状态

```
┌─────┐         ┌────────┐         ┌──────────┐
│User │         │FastAPI │         │PostgreSQL│
└──┬──┘         └───┬────┘         └────┬─────┘
   │                │                   │
   │ GET /monitoring/tasks               │
   │ + JWT Token                        │
   ├───────────────►│                   │
   │                │                   │
   │                │ Verify JWT        │
   │                │ Extract user_id   │
   │                │                   │
   │                │ SELECT tasks      │
   │                │ WHERE user_id=X   │
   │                ├──────────────────►│
   │                │                   │
   │                │ tasks list        │
   │                │◄──────────────────┤
   │                │                   │
   │ [tasks array]  │                   │
   │◄───────────────┤                   │
   │                │                   │
```

---

## 数据库设计

### ER 图

```
┌─────────────────┐
│     Users       │
├─────────────────┤
│ id (PK)         │
│ email (UNIQUE)  │
│ password_hash   │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         │
    ┌────┴─────────────────────────────┐
    │                                  │
    ▼                                  ▼
┌─────────────────────┐    ┌─────────────────────┐
│ MonitoringTasks     │    │ NotificationSettings│
├─────────────────────┤    ├─────────────────────┤
│ id (PK)             │    │ id (PK)             │
│ user_id (FK)        │    │ user_id (FK)        │
│ provider            │    │ notification_type   │
│ campground_id       │    │ config_data (JSON)  │
│ campground_name     │    │ is_enabled          │
│ start_date          │    │ created_at          │
│ end_date            │    │ updated_at          │
│ nights              │    └─────────────────────┘
│ search_mode         │
│ status              │
│ rq_job_id           │
│ last_checked_at     │
│ completed_at        │
│ error_message       │
│ created_at          │
│ updated_at          │
└──────┬──────────────┘
       │
       │ 1:N
       │
       ▼
┌─────────────────────┐    ┌─────────────────────┐
│ NotificationHistory │    │ FavoriteCampgrounds │
├─────────────────────┤    ├─────────────────────┤
│ id (PK)             │    │ id (PK)             │
│ user_id (FK)        │    │ user_id (FK)        │
│ task_id (FK)        │    │ provider            │
│ notification_type   │    │ campground_id       │
│ campground_name     │    │ campground_name     │
│ availability_data   │    │ created_at          │
│ sent_at             │    └─────────────────────┘
│ success             │
│ error_message       │
└─────────────────────┘
```

### 表详细设计

#### 1. users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**字段说明**:
- `id`: 自增主键
- `email`: 用户邮箱，唯一索引
- `password_hash`: bcrypt 哈希密码
- `created_at/updated_at`: 时间戳

#### 2. monitoring_tasks
```sql
CREATE TABLE monitoring_tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- 营地信息
    provider VARCHAR(100) NOT NULL,
    campground_id VARCHAR(50) NOT NULL,
    campground_name VARCHAR(255) NOT NULL,

    -- 搜索参数
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    nights INTEGER,  -- NULL = exact dates, >0 = range search
    search_mode VARCHAR(20) DEFAULT 'exact',

    -- 任务状态
    status VARCHAR(20) DEFAULT 'active',
    rq_job_id VARCHAR(255),

    -- 时间戳
    last_checked_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 错误信息
    error_message TEXT
);

CREATE INDEX idx_monitoring_tasks_user_id ON monitoring_tasks(user_id);
CREATE INDEX idx_monitoring_tasks_status ON monitoring_tasks(status);
CREATE INDEX idx_monitoring_tasks_active ON monitoring_tasks(user_id, status)
    WHERE status = 'active';
```

**状态流转**:
```
    created
       │
       ▼
   ┌───────┐      pause      ┌────────┐
   │active │◄────────────────┤ paused │
   └───┬───┘─────────────────►└────────┘
       │           resume
       │
       ├─────────► completed (found availability)
       │
       ├─────────► cancelled (user cancelled)
       │
       └─────────► failed (error occurred)
```

#### 3. notification_settings
```sql
CREATE TABLE notification_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,  -- email, pushover, telegram
    config_data JSONB NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id, notification_type)
);
```

**config_data 示例**:
```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "user@example.com"
  },
  "pushover": {
    "user_key": "xxx",
    "api_token": "xxx"
  }
}
```

#### 4. notification_history
```sql
CREATE TABLE notification_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES monitoring_tasks(id) ON DELETE SET NULL,
    notification_type VARCHAR(50) NOT NULL,
    campground_name VARCHAR(255) NOT NULL,
    availability_data JSONB NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

CREATE INDEX idx_notification_history_user_id ON notification_history(user_id);
CREATE INDEX idx_notification_history_sent_at ON notification_history(sent_at DESC);
```

---

## API设计

### RESTful 设计原则

- **资源导向**: 使用名词而非动词
- **HTTP 方法**: GET (查询), POST (创建), PATCH (部分更新), DELETE (删除)
- **状态码**: 200 (成功), 201 (创建), 400 (客户端错误), 401 (未认证), 404 (未找到), 500 (服务器错误)
- **版本控制**: 路径版本 (未来: /api/v2/)

### API 端点设计

#### 认证模块
```
POST   /auth/register          # 用户注册
POST   /auth/login             # 用户登录
GET    /auth/me                # 获取当前用户
```

#### 监控任务模块
```
POST   /monitoring/tasks              # 创建监控任务
GET    /monitoring/tasks              # 获取所有任务（支持过滤）
GET    /monitoring/tasks/{id}         # 获取单个任务
PATCH  /monitoring/tasks/{id}         # 更新任务（暂停/恢复/取消）
DELETE /monitoring/tasks/{id}         # 删除任务
GET    /monitoring/tasks/{id}/status  # 获取RQ作业状态
```

#### 通知模块
```
GET    /monitoring/notifications      # 获取通知历史
```

#### 即时搜索模块（无需认证）
```
GET    /api/providers                      # 获取供应商列表
GET    /api/campgrounds                    # 搜索营地
POST   /api/availability                   # 检查可用性
POST   /api/availability/search            # 多营地搜索
```

---

## 任务队列设计

### RQ 队列架构

```
┌────────────────────────────────────────┐
│          Redis (Message Broker)        │
│                                        │
│  Queue: monitoring                     │
│  ┌──────────────────────────────────┐  │
│  │ Job 1: check_campsite(task_id=1) │  │
│  │ Job 2: check_campsite(task_id=2) │  │
│  │ Job 3: check_campsite(task_id=3) │  │
│  └──────────────────────────────────┘  │
└─────────────┬──────────────────────────┘
              │
              ├──────────► Worker 1 (Process 1)
              │
              ├──────────► Worker 2 (Process 2) [可选]
              │
              └──────────► Worker N (Process N) [可选]
```

### 任务定义

**主任务**: `check_campsite_availability(task_id: int)`

```python
def check_campsite_availability(task_id: int) -> Dict[str, Any]:
    """
    检查营地可用性的后台任务

    执行流程:
    1. 从数据库读取任务详情
    2. 更新 last_checked_at
    3. 调用 Camply Provider 检查
    4. 如果可用:
       - 创建通知记录
       - 更新任务状态为 completed
    5. 如果不可用:
       - 继续保持 active 状态
    6. 如果出错:
       - 更新任务状态为 failed
       - 记录错误信息

    Returns:
        结果字典包含状态和信息
    """
```

### 任务调度策略

**当前实现**:
- 创建任务时立即执行一次
- 单次执行，不自动重试

**未来改进**:
1. **定时重复检查**:
   ```python
   # 每小时检查一次
   scheduler.enqueue_in(timedelta(hours=1), check_campsite_availability, task_id)
   ```

2. **优先级队列**:
   ```python
   # 高优先级任务
   queue.enqueue(check_campsite_availability, task_id, priority='high')
   ```

3. **失败重试**:
   ```python
   # 失败后重试3次
   queue.enqueue(check_campsite_availability, task_id, retry=Retry(max=3))
   ```

---

## 认证与授权

### JWT Token 结构

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user@example.com",  // 用户邮箱
    "exp": 1735689600            // 过期时间戳
  },
  "signature": "..."
}
```

### 认证流程

```
1. 用户登录 → 服务器验证密码
2. 生成 JWT token (有效期30分钟)
3. 客户端保存 token
4. 后续请求携带 token:
   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
5. 服务器验证 token 签名和过期时间
6. 提取用户信息，加载到请求上下文
```

### 权限控制

**当前**: 基于用户的资源隔离
- 用户只能查看/修改自己的监控任务
- 数据库查询自动过滤: `WHERE user_id = current_user.id`

**未来**: 基于角色的访问控制 (RBAC)
```python
roles = {
    'admin': ['*'],  # 所有权限
    'user': ['read:own_tasks', 'write:own_tasks'],
    'viewer': ['read:own_tasks']
}
```

---

## 扩展性考虑

### 1. 水平扩展

**API 服务器**:
```bash
# 使用 gunicorn 启动多个 worker
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

**RQ Worker**:
```bash
# 启动多个 worker 进程
rq worker monitoring &  # Worker 1
rq worker monitoring &  # Worker 2
rq worker monitoring &  # Worker 3
```

### 2. 数据库优化

**索引优化**:
- 复合索引: `(user_id, status)` 用于过滤活跃任务
- 部分索引: `WHERE status = 'active'` 减少索引大小

**分区表** (未来):
```sql
-- 按时间分区通知历史
CREATE TABLE notification_history_2026_01 PARTITION OF notification_history
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

### 3. 缓存策略

**Redis 缓存** (未来):
```python
# 缓存营地信息
cache.set(f"campground:{id}", data, expire=3600)

# 缓存用户任务列表
cache.set(f"user:{id}:tasks", tasks, expire=300)
```

### 4. 通知系统扩展

**通知通道**:
- Email (SMTP)
- Pushover (HTTP API)
- Telegram Bot (HTTP API)
- Webhook (自定义 URL)

**通知去重**:
```python
# 24小时内同一营地只通知一次
if not recently_notified(user_id, campground_id, hours=24):
    send_notification()
```

### 5. 监控与告警

**系统监控**:
- Prometheus + Grafana
- 监控指标:
  - API 请求延迟
  - 任务队列长度
  - Worker 处理速度
  - 数据库连接池

**日志聚合**:
- ELK Stack (Elasticsearch + Logstash + Kibana)
- 结构化日志

### 6. 高可用性

**数据库**:
- PostgreSQL 主从复制
- 读写分离

**Redis**:
- Redis Sentinel (故障转移)
- Redis Cluster (分片)

**负载均衡**:
```
          ┌──────────┐
          │ Nginx/   │
          │ HAProxy  │
          └────┬─────┘
               │
        ┌──────┼──────┐
        ▼      ▼      ▼
    API-1  API-2  API-3
```

---

## 安全考虑

### 1. 密码安全
- bcrypt 哈希 (cost factor = 12)
- 最小密码长度: 8 字符
- 密码复杂度验证 (未来)

### 2. SQL 注入防护
- 使用 SQLAlchemy ORM
- 参数化查询
- 输入验证

### 3. XSS 防护
- FastAPI 自动转义
- Content-Type 验证

### 4. CSRF 防护
- JWT token 不受 CSRF 影响
- SameSite Cookie (未来使用 Cookie 时)

### 5. 速率限制 (未来)
```python
@limiter.limit("5/minute")
def create_task():
    ...
```

### 6. 敏感信息
- `.env` 文件不提交到 Git
- SECRET_KEY 使用强随机值
- 生产环境使用环境变量

---

## 性能优化

### 1. 数据库查询
- N+1 查询优化: 使用 `joinedload`
- 分页查询: 避免全表扫描
- 索引优化

### 2. API 响应
- 压缩响应 (gzip)
- 分页返回大数据集
- 字段过滤 (只返回需要的字段)

### 3. 后台任务
- 批量处理
- 任务去重
- 超时控制

---

## 未来功能规划

### Phase 2
- [ ] 定时调度（每小时自动检查）
- [ ] Email 通知
- [ ] Pushover 通知

### Phase 3
- [ ] 前端管理界面
- [ ] WebSocket 实时通知
- [ ] 营地收藏功能
- [ ] 任务模板

### Phase 4
- [ ] 多用户协作
- [ ] 分享监控链接
- [ ] 营地推荐算法
- [ ] 价格追踪

---

## 总结

本系统采用现代化的微服务架构，使用成熟的技术栈，具有良好的扩展性和可维护性。通过合理的数据库设计、任务队列机制和认证授权系统，实现了高效、安全的营地监控服务。
