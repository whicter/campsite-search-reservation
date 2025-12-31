import React, { useState, useEffect } from 'react';
import './App.css';
import SearchForm from './components/SearchForm';
import ResultsDisplay from './components/ResultsDisplay';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Load providers on mount
  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/providers`);
      setProviders(response.data);
    } catch (err) {
      console.error('Error loading providers:', err);
      setError('Failed to load providers. Make sure the backend is running.');
    }
  };

  const handleSearch = async (searchParams) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // First, search for campgrounds
      const campgroundsResponse = await axios.get(`${API_URL}/api/campgrounds`, {
        params: {
          provider: searchParams.provider,
          search: searchParams.campgroundName
        }
      });

      if (campgroundsResponse.data.length === 0) {
        setError(`No campgrounds found for "${searchParams.campgroundName}"`);
        setLoading(false);
        return;
      }

      // Use the first campground result
      const campground = campgroundsResponse.data[0];

      // Now search for availability
      const availabilityResponse = await axios.post(`${API_URL}/api/availability`, {
        provider: searchParams.provider,
        campground_id: campground.id,
        nights: parseInt(searchParams.nights),
        search_days: 365
      });

      setResults(availabilityResponse.data);
    } catch (err) {
      console.error('Error searching:', err);
      setError(
        err.response?.data?.detail ||
        'Failed to search for availability. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>⛺ Campsite Search</h1>
          <p>Find available campsites across multiple reservation systems</p>
        </header>

        <SearchForm
          providers={providers}
          onSearch={handleSearch}
          loading={loading}
        />

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Searching for availability... This may take a moment.</p>
          </div>
        )}

        {results && !loading && (
          <ResultsDisplay results={results} />
        )}
      </div>
    </div>
  );
}

export default App;
