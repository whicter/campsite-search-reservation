import React, { useState, useEffect } from 'react';
import { monitoringAPI, campsiteAPI } from '../../utils/api';

const CreateTaskModal = ({ onClose, onTaskCreated, initialData = null }) => {
  const [providers, setProviders] = useState([]);
  const [formData, setFormData] = useState({
    provider: 'RecreationDotGov',
    campground_id: initialData?.campground_id || '',
    campground_name: initialData?.campground_name || '',
    start_date: '',
    end_date: '',
    search_mode: 'exact',
    nights: 1
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      const response = await campsiteAPI.getProviders();
      setProviders(response.data);
    } catch (err) {
      console.error('Failed to load providers:', err);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await monitoringAPI.createTask(formData);
      onTaskCreated();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create monitoring task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create Monitoring Task</h2>
          <button onClick={onClose} className="modal-close">&times;</button>
        </div>

        {error && (
          <div className="alert alert-error">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label>Provider</label>
            <select
              name="provider"
              value={formData.provider}
              onChange={handleChange}
              required
            >
              {providers.map(p => (
                <option key={p.name} value={p.name}>{p.display_name}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Campground ID</label>
            <input
              type="text"
              name="campground_id"
              value={formData.campground_id}
              onChange={handleChange}
              placeholder="e.g., 232448"
              required
            />
            <small>Find the ID from the search results</small>
          </div>

          <div className="form-group">
            <label>Campground Name</label>
            <input
              type="text"
              name="campground_name"
              value={formData.campground_name}
              onChange={handleChange}
              placeholder="e.g., Upper Pines Campground"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Start Date</label>
              <input
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>End Date</label>
              <input
                type="date"
                name="end_date"
                value={formData.end_date}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Search Mode</label>
            <select
              name="search_mode"
              value={formData.search_mode}
              onChange={handleChange}
            >
              <option value="exact">Exact Dates</option>
              <option value="range">Range Search</option>
            </select>
          </div>

          {formData.search_mode === 'range' && (
            <div className="form-group">
              <label>Number of Nights</label>
              <input
                type="number"
                name="nights"
                value={formData.nights}
                onChange={handleChange}
                min="1"
                required
              />
            </div>
          )}

          <div className="modal-footer">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Monitor'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateTaskModal;
