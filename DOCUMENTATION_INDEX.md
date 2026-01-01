# Documentation Index - 文档索引

## 📚 完整文档指南

欢迎！这里是 Campsite Search & Monitoring System 的完整文档索引。根据您的需求选择相应文档：

---

## 🎯 根据目的选择文档

### 我想要...

#### 🚀 快速开始 / 安装系统
→ **[SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)**
- 一键安装脚本
- 手动安装步骤
- 服务启动和停止
- 常见安装问题

#### 💡 了解如何使用 API
→ **[backend/API_USAGE.md](./backend/API_USAGE.md)**
- 所有 API 端点说明
- 完整的 curl 示例
- 工作流程示例
- 认证和授权说明

#### 🔧 开发和调试
→ **[backend/DEVELOPER.md](./backend/DEVELOPER.md)**
- 开发环境设置
- 数据库操作和查询
- Redis 和队列监控
- 调试技巧和测试指南
- 常见问题解决

#### 🏗️ 理解系统架构
→ **[backend/DESIGN.md](./backend/DESIGN.md)**
- 系统架构设计
- 数据流程图
- 数据库设计详解
- API 设计原则
- 扩展性考虑

#### ⚡ 快速查找命令
→ **[backend/QUICKREF.md](./backend/QUICKREF.md)**
- 常用命令速查
- API 测试命令
- 故障排查步骤
- SQL 查询示例

#### 📖 项目概览
→ **[backend/README.md](./backend/README.md)**
- 项目介绍和功能
- 技术栈
- 快速开始
- 项目结构

---

## 📑 按文档类型分类

### 1. 入门文档

| 文档 | 描述 | 适合人群 |
|------|------|----------|
| [backend/README.md](./backend/README.md) | 项目总览和快速开始 | 所有人 |
| [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md) | 详细安装指南 | 首次安装 |

### 2. 使用文档

| 文档 | 描述 | 适合人群 |
|------|------|----------|
| [backend/API_USAGE.md](./backend/API_USAGE.md) | API 使用文档 | API 用户、前端开发者 |
| [backend/QUICKREF.md](./backend/QUICKREF.md) | 快速参考 | 日常使用 |

### 3. 开发文档

| 文档 | 描述 | 适合人群 |
|------|------|----------|
| [backend/DEVELOPER.md](./backend/DEVELOPER.md) | 开发者指南 | 后端开发者 |
| [backend/DESIGN.md](./backend/DESIGN.md) | 系统设计文档 | 架构师、高级开发者 |

### 4. 数据库文档

| 文档 | 描述 | 适合人群 |
|------|------|----------|
| [backend/database_schema.sql](./backend/database_schema.sql) | 数据库 Schema | 数据库管理员 |

---

## 🔍 按主题查找

### 认证与授权
- **JWT 认证流程**: [DESIGN.md - 认证与授权](./backend/DESIGN.md#认证与授权)
- **API 使用示例**: [API_USAGE.md - 认证](./backend/API_USAGE.md#认证-authentication)
- **实现细节**: `backend/app/auth.py`

### 监控任务
- **工作流程**: [DESIGN.md - 数据流程](./backend/DESIGN.md#数据流程)
- **API 端点**: [API_USAGE.md - 监控任务](./backend/API_USAGE.md#监控任务-monitoring-tasks)
- **实现代码**: `backend/app/routers/monitoring.py`

### 后台任务队列
- **RQ 架构**: [DESIGN.md - 任务队列设计](./backend/DESIGN.md#任务队列设计)
- **监控队列**: [DEVELOPER.md - Redis与队列监控](./backend/DEVELOPER.md#redis与队列监控)
- **任务定义**: `backend/app/tasks.py`

### 数据库
- **表设计**: [DESIGN.md - 数据库设计](./backend/DESIGN.md#数据库设计)
- **操作指南**: [DEVELOPER.md - 数据库操作](./backend/DEVELOPER.md#数据库操作)
- **Schema**: [database_schema.sql](./backend/database_schema.sql)

### 调试和故障排查
- **调试技巧**: [DEVELOPER.md - 调试技巧](./backend/DEVELOPER.md#调试技巧)
- **常见问题**: [DEVELOPER.md - 常见问题](./backend/DEVELOPER.md#常见问题)
- **快速参考**: [QUICKREF.md - 故障排查](./backend/QUICKREF.md#故障排查)

---

## 📖 文档阅读路径推荐

### 路径 1: 新用户（只想使用）

1. **[backend/README.md](./backend/README.md)** - 了解项目
2. **[SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)** - 安装系统
3. **[backend/API_USAGE.md](./backend/API_USAGE.md)** - 学习使用 API
4. **[backend/QUICKREF.md](./backend/QUICKREF.md)** - 日常参考

### 路径 2: 开发者（参与开发）

1. **[backend/README.md](./backend/README.md)** - 项目概览
2. **[SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)** - 搭建环境
3. **[backend/DESIGN.md](./backend/DESIGN.md)** - 理解架构
4. **[backend/DEVELOPER.md](./backend/DEVELOPER.md)** - 开发工作流
5. **[backend/API_USAGE.md](./backend/API_USAGE.md)** - API 参考
6. **[backend/QUICKREF.md](./backend/QUICKREF.md)** - 快速查找

### 路径 3: 架构师（系统设计）

1. **[backend/README.md](./backend/README.md)** - 功能特性
2. **[backend/DESIGN.md](./backend/DESIGN.md)** - 完整架构设计
3. **[backend/database_schema.sql](./backend/database_schema.sql)** - 数据库 Schema
4. **[backend/DEVELOPER.md](./backend/DEVELOPER.md)** - 实现细节

---

## 🗂️ 文件位置总览

```
campsite-search-resevation/
│
├── DOCUMENTATION_INDEX.md          # 本文档 - 文档索引
├── SETUP_INSTRUCTIONS.md           # 安装指南
│
└── backend/
    ├── README.md                   # 项目总览
    ├── API_USAGE.md                # API 使用文档
    ├── DEVELOPER.md                # 开发者文档
    ├── DESIGN.md                   # 系统设计文档
    ├── QUICKREF.md                 # 快速参考
    ├── database_schema.sql         # 数据库 Schema
    │
    ├── setup_services.sh           # 安装脚本
    ├── start_services.sh           # 启动脚本
    ├── stop_services.sh            # 停止脚本
    │
    └── app/                        # 源代码
        ├── main.py
        ├── auth.py
        ├── tasks.py
        └── ...
```

---

## 💡 提示

### 快速搜索
在文档中使用浏览器搜索功能（Ctrl+F / Cmd+F）快速定位内容。

### 代码示例
所有文档中的代码示例都可以直接复制使用。

### 保持更新
文档会随着代码更新，建议定期查看最新版本。

---

## 🚀 快速操作

### 第一次使用？

```bash
# 1. 安装
cd backend
./setup_services.sh

# 2. 启动
./start_services.sh

# 3. 测试
curl http://localhost:8000/health
```

### 查看 API 文档
访问 http://localhost:8000/docs

### 获取帮助
遇到问题？按顺序查看：
1. [QUICKREF.md](./backend/QUICKREF.md) - 快速解决
2. [DEVELOPER.md - 常见问题](./backend/DEVELOPER.md#常见问题)
3. 查看日志: `tail -f backend/logs/*.log`

---

## 📞 联系和反馈

- **Bug 报告**: 创建 GitHub Issue
- **功能建议**: 创建 GitHub Issue
- **文档改进**: 提交 Pull Request

---

**最后更新**: 2025-12-31

**版本**: 2.0.0

**维护者**: Campsite Search Team
