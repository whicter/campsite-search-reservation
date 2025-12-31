# Campsite Search & Reservation System

A web application to search for available campsites across multiple reservation systems with a unified interface.

## Overview

This application provides a simple UI to search for campsite availability by entering:
- Campground name
- Provider (ReserveCalifornia, Recreation.gov, etc.)
- Number of nights

The system will return all available date combinations, e.g., for "New Brighton SB, 3 nights":
- 3/12 - 3/15
- 3/13 - 3/16
- etc.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (UI)                       │
│  - Campground search                                         │
│  - Provider dropdown                                         │
│  - Date range results display                                │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│              Python FastAPI Backend                          │
│                                                               │
│  ┌──────────────────┐         ┌─────────────────────────┐   │
│  │  Camply Provider │         │  Custom Crawlers        │   │
│  │  Integration     │         │  (Plugin Architecture)  │   │
│  ├──────────────────┤         ├─────────────────────────┤   │
│  │ - ReserveCalifornia        │ - San Mateo County      │   │
│  │ - Recreation.gov │         │ - Other custom systems  │   │
│  │ - GoingToCamp    │         │ - Extensible            │   │
│  └──────────────────┘         └─────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

## Why Python Backend?

### For Camply-Supported Providers
- **Direct API access**: Use camply Python library directly (not CLI)
- **Better performance**: No subprocess overhead
- **Structured data**: Native Python objects, no text parsing
- **Error handling**: Proper exception handling

### For Custom Providers (Not Supported by Camply)
- **Rich ecosystem**: Python has excellent web scraping libraries
  - `requests` - HTTP client
  - `BeautifulSoup` - HTML parsing
  - `Playwright` - Dynamic content handling
- **Unified codebase**: All crawlers in same language
- **Easy maintenance**: Add new providers as plugins

### Plugin Architecture
Each provider is an independent module:
- Camply-supported → Use camply library
- Custom systems → Write custom crawler
- Future providers → Easy to add

## Technology Stack

### Backend
- **Python 3.9+**
- **FastAPI** - Modern async web framework
- **camply** - Campsite availability library
- **requests** - HTTP client for custom crawlers

### Frontend
- **React** - UI framework
- **Axios** - HTTP client
- **Tailwind CSS** - Styling (optional)

## Project Structure

```
campsite-search-resevation/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── providers/           # Provider plugins
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Base provider interface
│   │   │   ├── camply_provider.py    # Camply integration
│   │   │   └── sanmateo_provider.py  # Custom crawler example
│   │   ├── models.py            # Data models
│   │   └── utils.py             # Utilities
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchForm.jsx
│   │   │   └── ResultsDisplay.jsx
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── .env.example
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- camply installed: `pip install camply`

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend will run on `http://localhost:3000`

## API Endpoints

### Get Supported Providers
```
GET /api/providers
Response: ["ReserveCalifornia", "Recreation.gov", "SanMateoCounty", ...]
```

### Search Campgrounds
```
GET /api/campgrounds?provider=ReserveCalifornia&search=New Brighton SB
Response: [
  {"id": "598", "name": "New Brighton SB - Northern End"},
  {"id": "597", "name": "New Brighton SB - Southern End"}
]
```

### Search Availability
```
POST /api/availability
Body: {
  "provider": "ReserveCalifornia",
  "campground_id": "598",
  "nights": 3,
  "search_days": 365
}
Response: [
  {"start_date": "2025-03-12", "end_date": "2025-03-15", "available": true},
  {"start_date": "2025-03-13", "end_date": "2025-03-16", "available": true},
  ...
]
```

## How It Works

1. **User Input**: Enter campground name, select provider, specify nights
2. **Backend Processing**:
   - Find campground ID using provider's search API
   - Scan next 365 days for consecutive available nights
   - Use camply for supported providers
   - Use custom crawler for unsupported systems
3. **Display Results**: Show all available date combinations

## Adding New Providers

To add a new provider, create a new file in `backend/app/providers/`:

```python
from .base import BaseProvider

class NewProvider(BaseProvider):
    def search_campgrounds(self, query: str):
        # Implementation
        pass

    def get_availability(self, campground_id: str, start_date: str, end_date: str):
        # Implementation
        pass
```

Register it in `backend/app/providers/__init__.py`.

## Features

- Search across multiple providers
- Find all available date combinations for specified nights
- Support for both camply-supported and custom systems
- Extensible plugin architecture
- Clean, modern UI

## Limitations & Notes

- Default search range: 365 days from today
- Camply guarantees same campsite for entire date range
- Custom crawlers respect rate limiting and robots.txt
- Some providers may require authentication

## Future Enhancements

- [ ] Email notifications for availability
- [ ] Save favorite campgrounds
- [ ] Continuous monitoring mode
- [ ] Calendar view of availability
- [ ] Direct booking links
- [ ] Mobile app

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
