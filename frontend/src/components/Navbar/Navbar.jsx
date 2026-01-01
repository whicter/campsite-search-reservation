import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, isAuthenticated, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          ⛺ Campsite Search
        </Link>

        <div className="navbar-menu">
          <Link to="/" className="navbar-link">
            Search
          </Link>

          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="navbar-link">
                Dashboard
              </Link>
              <Link to="/monitoring" className="navbar-link">
                My Monitors
              </Link>
              <Link to="/favorites" className="navbar-link">
                Favorites
              </Link>
              {isAdmin() && (
                <Link to="/admin" className="navbar-link navbar-admin">
                  Admin
                </Link>
              )}
              <div className="navbar-user">
                <span className="user-email">{user?.email}</span>
                <button onClick={handleLogout} className="btn-logout">
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="navbar-link">
                Login
              </Link>
              <Link to="/register" className="btn btn-primary-nav">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
