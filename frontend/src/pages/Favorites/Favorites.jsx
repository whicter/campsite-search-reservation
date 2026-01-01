import React from 'react';
import './Favorites.css';

const Favorites = () => {
  return (
    <div className="favorites-page">
      <div className="page-header">
        <h1>⭐ Favorite Campgrounds</h1>
        <p>Your saved campgrounds (Coming Soon)</p>
      </div>

      <div className="coming-soon">
        <div className="coming-soon-icon">🏕️</div>
        <h2>Favorites Feature Coming Soon</h2>
        <p>You'll soon be able to save your favorite campgrounds and quickly create monitoring tasks for them.</p>

        <div className="feature-list">
          <h3>Planned Features:</h3>
          <ul>
            <li>✨ Save campgrounds from search results</li>
            <li>✨ Quick monitor creation from favorites</li>
            <li>✨ Organize favorites by location or type</li>
            <li>✨ Share favorite lists with friends</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Favorites;
