import React, { useState } from 'react';
import './SearchForm.css';

function SearchForm({ providers, onSearch, loading }) {
  const [formData, setFormData] = useState({
    provider: '',
    campgroundName: '',
    nights: '2'
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!formData.provider || !formData.campgroundName || !formData.nights) {
      alert('Please fill in all fields');
      return;
    }

    if (parseInt(formData.nights) < 1 || parseInt(formData.nights) > 14) {
      alert('Number of nights must be between 1 and 14');
      return;
    }

    onSearch(formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <form className="search-form" onSubmit={handleSubmit}>
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
      </div>

      <button type="submit" className="search-button" disabled={loading}>
        {loading ? 'Searching...' : 'Search Availability'}
      </button>

      <p className="help-text">
        We'll search the next 365 days for available {formData.nights || '___'}-night stays
      </p>
    </form>
  );
}

export default SearchForm;
