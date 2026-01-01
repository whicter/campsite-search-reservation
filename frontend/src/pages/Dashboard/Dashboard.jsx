import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="dashboard-page">
      <div className="dashboard-hero">
        <h1>Welcome back, {user?.email}! 👋</h1>
        <p>Manage your campsite monitoring and find your perfect camping spot</p>
      </div>

      <div className="quick-actions">
        <Link to="/monitoring" className="action-card">
          <div className="action-icon">📊</div>
          <h3>My Monitors</h3>
          <p>View and manage your monitoring tasks</p>
        </Link>

        <Link to="/" className="action-card">
          <div className="action-icon">🔍</div>
          <h3>Search Campsites</h3>
          <p>Find available campsites instantly</p>
        </Link>

        <Link to="/favorites" className="action-card">
          <div className="action-icon">⭐</div>
          <h3>Favorites</h3>
          <p>Your saved campgrounds</p>
        </Link>
      </div>

      <div className="dashboard-info">
        <div className="info-section">
          <h2>Quick Start Guide</h2>
          <ol>
            <li>Search for campsites using the search page</li>
            <li>Create a monitoring task for your desired dates</li>
            <li>Get notified when spots become available</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
