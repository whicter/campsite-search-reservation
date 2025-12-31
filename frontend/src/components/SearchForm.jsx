import React, { useState } from 'react';
import './SearchForm.css';

function SearchForm({ providers, onSearch, loading }) {
  // Get today's date in YYYY-MM-DD format
  const today = new Date().toISOString().split('T')[0];
  // Get tomorrow's date
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const tomorrowStr = tomorrow.toISOString().split('T')[0];

  const [searchMode, setSearchMode] = useState('exact'); // 'exact' or 'range'
  const [formData, setFormData] = useState({
    provider: '',
    campgroundName: '',
    startDate: today,
    endDate: tomorrowStr,
    nights: 2
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!formData.provider || !formData.campgroundName || !formData.startDate || !formData.endDate) {
      alert('Please fill in all fields');
      return;
    }

    // Validate dates
    const start = new Date(formData.startDate);
    const end = new Date(formData.endDate);

    if (end <= start) {
      alert('End date must be after start date');
      return;
    }

    if (start < new Date(today)) {
      alert('Start date cannot be in the past');
      return;
    }

    // Validate nights for range mode
    if (searchMode === 'range') {
      if (!formData.nights || formData.nights < 1) {
        alert('Please specify number of nights (at least 1)');
        return;
      }
    }

    onSearch({ ...formData, searchMode });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      {/* Search Mode Selector */}
      <div className="search-mode-selector">
        <label className="mode-option">
          <input
            type="radio"
            name="searchMode"
            value="exact"
            checked={searchMode === 'exact'}
            onChange={(e) => setSearchMode(e.target.value)}
            disabled={loading}
          />
          <span className="mode-label">
            <strong>Exact Dates</strong>
            <span className="mode-description">Check specific check-in and check-out dates</span>
          </span>
        </label>
        <label className="mode-option">
          <input
            type="radio"
            name="searchMode"
            value="range"
            checked={searchMode === 'range'}
            onChange={(e) => setSearchMode(e.target.value)}
            disabled={loading}
          />
          <span className="mode-label">
            <strong>Date Range Search</strong>
            <span className="mode-description">Find any available stays within a date range</span>
          </span>
        </label>
      </div>

      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="provider">Provider</label>
          <select
            id="provider"
            name="provider"
            value={formData.provider}
            onChange={handleChange}
            disabled={loading}
            required
          >
            <option value="">Select a provider...</option>
            {providers.map((provider) => (
              <option key={provider.name} value={provider.name}>
                {provider.display_name}
                {provider.supported_by_camply ? ' ✓' : ' (Custom)'}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="campgroundName">Campground Name</label>
          <input
            type="text"
            id="campgroundName"
            name="campgroundName"
            value={formData.campgroundName}
            onChange={handleChange}
            placeholder="e.g., New Brighton SB"
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="startDate">
            {searchMode === 'exact' ? 'Check-in Date' : 'Search Range Start'}
          </label>
          <input
            type="date"
            id="startDate"
            name="startDate"
            value={formData.startDate}
            onChange={handleChange}
            min={today}
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="endDate">
            {searchMode === 'exact' ? 'Check-out Date' : 'Search Range End'}
          </label>
          <input
            type="date"
            id="endDate"
            name="endDate"
            value={formData.endDate}
            onChange={handleChange}
            min={formData.startDate || today}
            disabled={loading}
            required
          />
        </div>

        {searchMode === 'range' && (
          <div className="form-group">
            <label htmlFor="nights">Number of Nights</label>
            <input
              type="number"
              id="nights"
              name="nights"
              value={formData.nights}
              onChange={handleChange}
              min="1"
              max="14"
              disabled={loading}
              required
            />
          </div>
        )}
      </div>

      <button type="submit" className="search-button" disabled={loading}>
        {loading ? 'Searching...' : 'Check Availability'}
      </button>

      <p className="help-text">
        {searchMode === 'exact' ? (
          formData.startDate && formData.endDate
            ? `Checking ${Math.ceil((new Date(formData.endDate) - new Date(formData.startDate)) / (1000 * 60 * 60 * 24))} night(s) from ${formData.startDate} to ${formData.endDate}`
            : 'Select your check-in and check-out dates'
        ) : (
          formData.startDate && formData.endDate && formData.nights
            ? `Searching for ${formData.nights}-night stays between ${formData.startDate} and ${formData.endDate}`
            : 'Select date range and number of nights'
        )}
      </p>
    </form>
  );
}

export default SearchForm;
