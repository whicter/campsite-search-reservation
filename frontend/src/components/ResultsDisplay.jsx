import React from 'react';
import './ResultsDisplay.css';

function ResultsDisplay({ results }) {
  const formatDate = (dateString) => {
    // Parse date string as local date to avoid timezone issues
    // dateString is in format: YYYY-MM-DD
    const [year, month, day] = dateString.split('-').map(Number);
    const date = new Date(year, month - 1, day); // month is 0-indexed

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (!results) {
    return null;
  }

  // Check if this is multi-campground results
  const isMultiResults = results.results && Array.isArray(results.results);

  if (isMultiResults) {
    return (
      <div className="results-container">
        <div className="results-header">
          <h2>
            {results.campgrounds_with_availability > 0 ? '✅ Found Availability!' : '❌ No Availability'}
          </h2>
          <div className="results-summary">
            <p>
              Searched {results.total_campgrounds_searched} campground{results.total_campgrounds_searched > 1 ? 's' : ''} for <strong>"{results.search_query}"</strong>
            </p>
            {results.search_mode === 'range' && (
              <p className="search-mode-info">
                🔍 Range Search: Looking for {results.results[0]?.nights}-night stays between {formatDate(results.results[0]?.start_date)} and {formatDate(results.results[0]?.end_date)}
              </p>
            )}
          </div>
        </div>

        <div className="multi-results">
          {results.results.map((result, index) => (
            <CampgroundResult key={index} result={result} formatDate={formatDate} />
          ))}
        </div>

        {results.campgrounds_with_availability === 0 && (
          <div className="suggestions">
            <p className="suggestion-title">Suggestions:</p>
            <ul>
              <li>Try different dates</li>
              {results.search_mode === 'range' && <li>Try fewer nights or a wider date range</li>}
              <li>Try a different campground</li>
              <li>Set up notifications for when it becomes available</li>
            </ul>
          </div>
        )}
      </div>
    );
  }

  // Single campground result (backward compatibility)
  const nights = Math.ceil((new Date(results.end_date) - new Date(results.start_date)) / (1000 * 60 * 60 * 24));

  return (
    <div className="results-container">
      <div className="results-header">
        <h2>{results.available ? '✅ Available!' : '❌ Not Available'}</h2>
        <div className="results-info">
          <p className="campground-name">{results.campground_name}</p>
        </div>
      </div>

      <div className={`availability-card ${results.available ? 'available' : 'unavailable'}`}>
        <div className="date-range">
          <div className="date-block">
            <span className="date-label">Check-in</span>
            <span className="date-value">{formatDate(results.start_date)}</span>
          </div>
          <div className="arrow">→</div>
          <div className="date-block">
            <span className="date-label">Check-out</span>
            <span className="date-value">{formatDate(results.end_date)}</span>
          </div>
        </div>
        <div className="nights-badge">
          {nights} night{nights > 1 ? 's' : ''}
        </div>
        <div className="message">
          {results.message}
        </div>

        {results.available && results.reservation_url && (
          <div className="reservation-section">
            <a
              href={results.reservation_url}
              target="_blank"
              rel="noopener noreferrer"
              className="reservation-button"
            >
              Reserve Now →
            </a>
            <p className="reservation-note">
              ⚠️ Remember to select your dates ({formatDate(results.start_date)} - {formatDate(results.end_date)}) on the reservation website
            </p>
          </div>
        )}
      </div>

      {!results.available && (
        <div className="suggestions">
          <p className="suggestion-title">Suggestions:</p>
          <ul>
            <li>Try different dates</li>
            <li>Try a shorter stay</li>
            <li>Check another campground</li>
            <li>Set up notifications for when it becomes available</li>
          </ul>
        </div>
      )}
    </div>
  );
}

// Component for individual campground result
function CampgroundResult({ result, formatDate }) {
  const nights = result.nights || Math.ceil((new Date(result.end_date) - new Date(result.start_date)) / (1000 * 60 * 60 * 24));

  return (
    <div className={`campground-result ${result.available ? 'available' : 'unavailable'}`}>
      <div className="campground-header">
        <div className="header-left">
          <h3>
            {result.available ? '✅' : '❌'} {result.campground_name}
          </h3>
          <span className="campground-id">ID: {result.campground_id}</span>
        </div>
        {result.nights && (
          <div className="nights-badge-header">
            {result.nights} night{result.nights > 1 ? 's' : ''}
          </div>
        )}
      </div>

      <div className="date-range">
        <div className="date-block">
          <span className="date-label">
            {result.nights ? 'Search Range' : 'Check-in'}
          </span>
          <span className="date-value">{formatDate(result.start_date)}</span>
        </div>
        <div className="arrow">→</div>
        <div className="date-block">
          <span className="date-label">
            {result.nights ? 'Through' : 'Check-out'}
          </span>
          <span className="date-value">{formatDate(result.end_date)}</span>
        </div>
      </div>

      <div className="message">
        {result.message}
      </div>

      {/* Show detailed availability for range searches */}
      {result.available && result.availability_details && result.availability_details.total_dates > 0 && (
        <div className="availability-details">
          <h4>📅 Available Dates ({result.availability_details.total_dates} dates found)</h4>
          <div className="available-dates-list">
            {result.availability_details.available_dates.map((dateInfo, idx) => (
              <div key={idx} className="date-item">
                <span className="date-text">{dateInfo.date}</span>
                <span className="site-count">{dateInfo.site_count} site{dateInfo.site_count > 1 ? 's' : ''}</span>
              </div>
            ))}
          </div>

          {/* Show campsite IDs if available */}
          {result.availability_details.campsites && result.availability_details.campsites.length > 0 && (
            <div className="campsites-section">
              <h4>🏕️ Available Campsites ({result.availability_details.total_unique_sites} unique sites)</h4>
              <div className="campsites-list">
                {result.availability_details.campsites.map((site, idx) => (
                  <div key={idx} className="campsite-item">
                    <span className="site-id">#{site.site_id}</span>
                    <span className="site-name">{site.site_name}</span>
                  </div>
                ))}
                {result.availability_details.total_unique_sites > result.availability_details.campsites.length && (
                  <p className="more-sites">
                    + {result.availability_details.total_unique_sites - result.availability_details.campsites.length} more sites...
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {result.available && result.reservation_url && (
        <div className="reservation-section">
          <a
            href={result.reservation_url}
            target="_blank"
            rel="noopener noreferrer"
            className="reservation-button"
          >
            Reserve Now →
          </a>
          <p className="reservation-note">
            ⚠️ Remember to select your dates on the reservation website
          </p>
        </div>
      )}
    </div>
  );
}

export default ResultsDisplay;
