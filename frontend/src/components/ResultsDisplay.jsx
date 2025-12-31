import React from 'react';
import './ResultsDisplay.css';

function ResultsDisplay({ results }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (!results || results.total_available === 0) {
    return (
      <div className="results-container">
        <div className="no-results">
          <h2>No Availability Found</h2>
          <p>
            No available {results?.nights}-night stays found for {results?.campground_name} in the next 365 days.
          </p>
          <p className="suggestion">Try:</p>
          <ul>
            <li>Different dates (search refreshes daily)</li>
            <li>Fewer nights</li>
            <li>A different campground</li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="results-container">
      <div className="results-header">
        <h2>Available Dates</h2>
        <div className="results-info">
          <p className="campground-name">{results.campground_name}</p>
          <p className="results-summary">
            Found <strong>{results.total_available}</strong> available {results.nights}-night stay(s)
          </p>
        </div>
      </div>

      <div className="results-grid">
        {results.results.map((result, index) => (
          <div key={index} className="result-card">
            <div className="date-range">
              <div className="date-block">
                <span className="date-label">Check-in</span>
                <span className="date-value">{formatDate(result.start_date)}</span>
              </div>
              <div className="arrow">→</div>
              <div className="date-block">
                <span className="date-label">Check-out</span>
                <span className="date-value">{formatDate(result.end_date)}</span>
              </div>
            </div>
            <div className="nights-badge">
              {results.nights} night{results.nights > 1 ? 's' : ''}
            </div>
          </div>
        ))}
      </div>

      {results.total_available > 10 && (
        <div className="results-note">
          Showing all {results.total_available} available date ranges
        </div>
      )}
    </div>
  );
}

export default ResultsDisplay;
