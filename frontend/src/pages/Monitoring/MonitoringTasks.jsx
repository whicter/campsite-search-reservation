import React, { useState, useEffect } from 'react';
import { monitoringAPI } from '../../utils/api';
import CreateTaskModal from './CreateTaskModal';
import './Monitoring.css';

const MonitoringTasks = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    loadTasks();
  }, [filterStatus]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const response = await monitoringAPI.getTasks(
        filterStatus !== 'all' ? filterStatus : null
      );
      setTasks(response.data);
    } catch (err) {
      setError('Failed to load monitoring tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this monitoring task?')) {
      return;
    }

    try {
      await monitoringAPI.deleteTask(taskId);
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (err) {
      alert('Failed to delete task');
      console.error(err);
    }
  };

  const handleUpdateStatus = async (taskId, newStatus) => {
    try {
      await monitoringAPI.updateTask(taskId, { status: newStatus });
      loadTasks();
    } catch (err) {
      alert('Failed to update task status');
      console.error(err);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      active: { class: 'status-active', text: 'Active' },
      paused: { class: 'status-paused', text: 'Paused' },
      completed: { class: 'status-completed', text: 'Completed' },
      cancelled: { class: 'status-cancelled', text: 'Cancelled' },
      failed: { class: 'status-failed', text: 'Failed' }
    };
    const badge = badges[status] || badges.active;
    return <span className={`status-badge ${badge.class}`}>{badge.text}</span>;
  };

  const filteredTasks = tasks;

  return (
    <div className="monitoring-page">
      <div className="page-header">
        <div>
          <h1>Monitoring Tasks</h1>
          <p>Manage your campsite availability monitors</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary"
        >
          + Create Monitor
        </button>
      </div>

      <div className="filter-bar">
        <button
          className={`filter-btn ${filterStatus === 'all' ? 'active' : ''}`}
          onClick={() => setFilterStatus('all')}
        >
          All Tasks ({tasks.length})
        </button>
        <button
          className={`filter-btn ${filterStatus === 'active' ? 'active' : ''}`}
          onClick={() => setFilterStatus('active')}
        >
          Active
        </button>
        <button
          className={`filter-btn ${filterStatus === 'paused' ? 'active' : ''}`}
          onClick={() => setFilterStatus('paused')}
        >
          Paused
        </button>
        <button
          className={`filter-btn ${filterStatus === 'completed' ? 'active' : ''}`}
          onClick={() => setFilterStatus('completed')}
        >
          Completed
        </button>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading tasks...</p>
        </div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : filteredTasks.length === 0 ? (
        <div className="empty-state">
          <h3>No monitoring tasks yet</h3>
          <p>Create your first monitor to get notified when campsites become available</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn btn-primary"
          >
            Create Monitor
          </button>
        </div>
      ) : (
        <div className="tasks-grid">
          {filteredTasks.map((task) => (
            <div key={task.id} className="task-card">
              <div className="task-header">
                <h3>{task.campground_name}</h3>
                {getStatusBadge(task.status)}
              </div>

              <div className="task-details">
                <div className="task-detail">
                  <span className="label">Provider:</span>
                  <span>{task.provider}</span>
                </div>
                <div className="task-detail">
                  <span className="label">Dates:</span>
                  <span>{task.start_date} → {task.end_date}</span>
                </div>
                <div className="task-detail">
                  <span className="label">Mode:</span>
                  <span>{task.search_mode === 'exact' ? 'Exact Dates' : `${task.nights} Nights`}</span>
                </div>
                {task.last_checked_at && (
                  <div className="task-detail">
                    <span className="label">Last Checked:</span>
                    <span>{new Date(task.last_checked_at).toLocaleString()}</span>
                  </div>
                )}
              </div>

              {task.error_message && (
                <div className="task-error">
                  Error: {task.error_message}
                </div>
              )}

              <div className="task-actions">
                {task.status === 'active' && (
                  <button
                    onClick={() => handleUpdateStatus(task.id, 'paused')}
                    className="btn btn-secondary btn-sm"
                  >
                    Pause
                  </button>
                )}
                {task.status === 'paused' && (
                  <button
                    onClick={() => handleUpdateStatus(task.id, 'active')}
                    className="btn btn-primary btn-sm"
                  >
                    Resume
                  </button>
                )}
                <button
                  onClick={() => handleDelete(task.id)}
                  className="btn btn-danger btn-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <CreateTaskModal
          onClose={() => setShowCreateModal(false)}
          onTaskCreated={loadTasks}
        />
      )}
    </div>
  );
};

export default MonitoringTasks;
