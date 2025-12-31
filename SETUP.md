# Setup Guide

This guide will walk you through setting up the Campsite Search application.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org/)
- **pip** (comes with Python)
- **camply** - Install with `pip install camply`

### Verify Prerequisites

```bash
python --version   # Should be 3.9+
node --version     # Should be 16+
npm --version
camply --version   # Should show camply is installed
```

## Step 1: Clone or Download the Project

If you haven't already, navigate to the project directory:

```bash
cd /Users/cohan/Documents/campsite-search-resevation
```

## Step 2: Backend Setup

### 2.1 Create Virtual Environment

```bash
cd backend
python -m venv venv
```

### 2.2 Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI - Web framework
- uvicorn - ASGI server
- camply - Campsite availability library
- requests - HTTP client
- beautifulsoup4 - HTML parsing
- Other dependencies

### 2.4 Configure Environment (Optional)

```bash
cp .env.example .env
```

Edit `.env` if you want to customize:
- API host/port
- CORS origins
- Email notifications (future feature)

### 2.5 Test Backend

```bash
python -m app.main
```

Or:

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Visit `http://localhost:8000` in your browser to verify.

## Step 3: Frontend Setup

Open a **new terminal window** (keep backend running).

### 3.1 Navigate to Frontend

```bash
cd /Users/cohan/Documents/campsite-search-resevation/frontend
```

### 3.2 Install Dependencies

```bash
npm install
```

This will install:
- React
- axios
- react-scripts
- Other dependencies

### 3.3 Configure Environment

```bash
cp .env.example .env
```

The `.env` file should contain:
```
REACT_APP_API_URL=http://localhost:8000
```

### 3.4 Start Frontend

```bash
npm start
```

This will:
- Start the development server
- Open `http://localhost:3000` in your browser automatically

## Step 4: Verify Everything Works

You should now have:

1. **Backend** running on `http://localhost:8000`
2. **Frontend** running on `http://localhost:3000`

### Quick Test

1. Open `http://localhost:3000` in your browser
2. Select "Reserve California" from the provider dropdown
3. Enter "New Brighton" in the campground name
4. Set nights to "2"
5. Click "Search Availability"

If everything is set up correctly, you should see a search in progress.

## Troubleshooting

### Backend Issues

**Issue: `ModuleNotFoundError: No module named 'fastapi'`**
- Solution: Make sure virtual environment is activated and run `pip install -r requirements.txt`

**Issue: `Command 'camply' not found`**
- Solution: Install camply: `pip install camply`

**Issue: `Port 8000 already in use`**
- Solution: Kill the process using port 8000 or change the port in `.env`

### Frontend Issues

**Issue: `npm: command not found`**
- Solution: Install Node.js from https://nodejs.org/

**Issue: `Failed to fetch providers`**
- Solution: Make sure backend is running on `http://localhost:8000`

**Issue: CORS errors**
- Solution: Check that `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`

### Camply Issues

**Issue: Camply commands timeout or fail**
- Solution: Check internet connection; some providers may be slow
- Try running camply directly: `camply campgrounds --provider ReserveCalifornia --search "Yosemite"`

## Next Steps

- Read [README.md](README.md) for architecture details
- See [USAGE.md](USAGE.md) for how to use the application
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for adding new providers

## Running in Production

For production deployment:

### Backend

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
npm run build
# Serve the build/ directory with nginx or similar
```

See deployment guides for Docker, AWS, Heroku, etc.
