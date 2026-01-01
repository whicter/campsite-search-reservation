import React, { useState, useEffect } from 'react';
import { adminAPI, monitoringAPI } from '../../utils/api';
import './Admin.css';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalTasks: 0,
    activeTasks: 0,
    completedTasks: 0
  });
  const [allTasks, setAllTasks] = useState([]);
  const [queueStatus, setQueueStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAdminData();
    // Refresh every 10 seconds
    const interval = setInterval(loadAdminData, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadAdminData = async () => {
    try {
      // For now, we'll load all tasks since we don't have admin-specific endpoints yet
      const tasksResponse = await monitoringAPI.getTasks();
      const tasks = tasksResponse.data;

      setAllTasks(tasks);
      setStats({
        totalUsers: new Set(tasks.map(t => t.user_id)).size,
        totalTasks: tasks.length,
        activeTasks: tasks.filter(t => t.status === 'active').length,
        completedTasks: tasks.filter(t => t.status === 'completed').length
      });

      setLoading(false);
    } catch (err) {
      console.error('Failed to load admin data:', err);
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      active: '#4caf50',
      paused: '#ff9800',
      completed: '#2196f3',
      failed: '#f44336',
      cancelled: '#9e9e9e'
    };
    return colors[status] || '#9e9e9e';
  };

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>🔧 Admin Dashboard</h1>
        <p>System monitoring and management</p>
        <div className="last-updated">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-value">{stats.totalUsers}</div>
            <div className="stat-label">Total Users</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-value">{stats.totalTasks}</div>
            <div className="stat-label">Total Tasks</div>
          </div>
        </div>

        <div className="stat-card stat-active">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <div className="stat-value">{stats.activeTasks}</div>
            <div className="stat-label">Active Monitors</div>
          </div>
        </div>

        <div className="stat-card stat-completed">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-value">{stats.completedTasks}</div>
            <div className="stat-label">Completed</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="admin-tabs">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab-btn ${activeTab === 'tasks' ? 'active' : ''}`}
          onClick={() => setActiveTab('tasks')}
        >
          All Tasks
        </button>
        <button
          className={`tab-btn ${activeTab === 'queue' ? 'active' : ''}`}
          onClick={() => setActiveTab('queue')}
        >
          Queue Status
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="admin-section">
          <h2>System Overview</h2>

          <div className="overview-grid">
            <div className="overview-card">
              <h3>Task Status Distribution</h3>
              <div className="status-distribution">
                {Object.entries(
                  allTasks.reduce((acc, task) => {
                    acc[task.status] = (acc[task.status] || 0) + 1;
                    return acc;
                  }, {})
                ).map(([status, count]) => (
                  <div key={status} className="status-row">
                    <span className="status-label" style={{ color: getStatusColor(status) }}>
                      ● {status}
                    </span>
                    <span className="status-count">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="overview-card">
              <h3>Recent Activity</h3>
              <div className="activity-list">
                {allTasks
                  .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                  .slice(0, 5)
                  .map(task => (
                    <div key={task.id} className="activity-item">
                      <div className="activity-icon">📌</div>
                      <div className="activity-content">
                        <div className="activity-title">{task.campground_name}</div>
                        <div className="activity-time">
                          {new Date(task.created_at).toLocaleString()}
                        </div>
                      </div>
                      <span
                        className="activity-status"
                        style={{ color: getStatusColor(task.status) }}
                      >
                        {task.status}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'tasks' && (
        <div className="admin-section">
          <h2>All Monitoring Tasks</h2>
          <div className="admin-table-container">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>User ID</th>
                  <th>Campground</th>
                  <th>Provider</th>
                  <th>Dates</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Last Checked</th>
                </tr>
              </thead>
              <tbody>
                {allTasks.map(task => (
                  <tr key={task.id}>
                    <td>{task.id}</td>
                    <td>{task.user_id}</td>
                    <td>{task.campground_name}</td>
                    <td>{task.provider}</td>
                    <td>
                      {task.start_date} → {task.end_date}
                    </td>
                    <td>
                      <span
                        className="table-status-badge"
                        style={{
                          background: getStatusColor(task.status) + '20',
                          color: getStatusColor(task.status)
                        }}
                      >
                        {task.status}
                      </span>
                    </td>
                    <td>{new Date(task.created_at).toLocaleString()}</td>
                    <td>
                      {task.last_checked_at
                        ? new Date(task.last_checked_at).toLocaleString()
                        : 'Never'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'queue' && (
        <div className="admin-section">
          <h2>Queue Status</h2>
          <div className="queue-info">
            <div className="info-card">
              <h3>Redis Queue</h3>
              <p>To view detailed queue status, use the RQ Dashboard:</p>
              <code>./campsite-env/bin/rq-dashboard --redis-url redis://localhost:6379/0</code>
              <p>Then visit: <a href="http://localhost:9181" target="_blank" rel="noopener noreferrer">http://localhost:9181</a></p>
            </div>

            <div className="info-card">
              <h3>Queue Commands</h3>
              <pre className="code-block">
{`# View queue status
./campsite-env/bin/rq info --url redis://localhost:6379/0

# View workers
redis-cli SMEMBERS rq:workers

# View queue length
redis-cli LLEN rq:queue:monitoring`}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
