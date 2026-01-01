-- Campsite Search Application Database Schema
-- PostgreSQL

-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 监控任务表
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
    search_mode VARCHAR(20) DEFAULT 'exact',  -- 'exact' or 'range'

    -- 任务状态
    status VARCHAR(20) DEFAULT 'active',  -- active, paused, completed, cancelled, failed
    rq_job_id VARCHAR(255),  -- RQ任务ID

    -- 时间戳
    last_checked_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 错误信息
    error_message TEXT
);

-- 通知配置表
CREATE TABLE notification_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- 通知类型
    notification_type VARCHAR(50) NOT NULL,  -- email, pushover, telegram

    -- 配置数据（JSON）
    config_data JSONB NOT NULL,

    -- 是否启用
    is_enabled BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 每个用户每种类型只能有一个配置
    UNIQUE(user_id, notification_type)
);

-- 通知历史表
CREATE TABLE notification_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES monitoring_tasks(id) ON DELETE SET NULL,

    -- 通知内容
    notification_type VARCHAR(50) NOT NULL,
    campground_name VARCHAR(255) NOT NULL,
    availability_data JSONB NOT NULL,

    -- 发送状态
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- 收藏营地表
CREATE TABLE favorite_campgrounds (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    provider VARCHAR(100) NOT NULL,
    campground_id VARCHAR(50) NOT NULL,
    campground_name VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 每个用户每个营地只能收藏一次
    UNIQUE(user_id, provider, campground_id)
);

-- 索引
CREATE INDEX idx_monitoring_tasks_user_id ON monitoring_tasks(user_id);
CREATE INDEX idx_monitoring_tasks_status ON monitoring_tasks(status);
CREATE INDEX idx_monitoring_tasks_active ON monitoring_tasks(user_id, status) WHERE status = 'active';
CREATE INDEX idx_notification_history_user_id ON notification_history(user_id);
CREATE INDEX idx_notification_history_sent_at ON notification_history(sent_at DESC);
CREATE INDEX idx_favorite_campgrounds_user_id ON favorite_campgrounds(user_id);

-- 更新时间戳触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_monitoring_tasks_updated_at BEFORE UPDATE ON monitoring_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_settings_updated_at BEFORE UPDATE ON notification_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
