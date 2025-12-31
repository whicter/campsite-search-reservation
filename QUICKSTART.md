# Quick Start Guide

Get the Campsite Search app running in 5 minutes!

## Prerequisites Check

```bash
python --version   # Need 3.9+
node --version     # Need 16+
```

Don't have them? See [SETUP.md](SETUP.md) for installation instructions.

## 1. Backend Setup (2 minutes)

```bash
cd /Users/cohan/Documents/campsite-search-resevation/backend

# Create virtual environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend
python -m app.main
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Leave this running! ✅

## 2. Frontend Setup (2 minutes)

Open a **new terminal window**, then:

```bash
cd /Users/cohan/Documents/campsite-search-resevation/frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start frontend
npm start
```

**Expected:** Browser opens to `http://localhost:3000` ✅

## 3. Test It! (1 minute)

In the browser:
1. **Provider**: Select "Reserve California"
2. **Campground**: Type "New Brighton"
3. **Nights**: Enter "2"
4. Click **Search Availability**

You should see search results! 🎉

## Using the Startup Scripts

Instead of manual commands, use the scripts:

**Terminal 1 (Backend):**
```bash
./start-backend.sh
```

**Terminal 2 (Frontend):**
```bash
./start-frontend.sh
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'fastapi'"**
→ Run `pip install -r requirements.txt` in backend/

**"npm: command not found"**
→ Install Node.js from https://nodejs.org

**"Port 8000 already in use"**
→ Kill the process: `lsof -ti:8000 | xargs kill -9`

**Backend won't start**
→ Make sure virtual environment is activated (you should see `(venv)` in prompt)

**Frontend can't connect to backend**
→ Check `http://localhost:8000` in browser - should see API info

## What's Next?

- Read [USAGE.md](USAGE.md) to learn how to use the app
- Read [README.md](README.md) to understand the architecture
- See [SETUP.md](SETUP.md) for detailed setup instructions

## Daily Use

Once set up, to run the app:

**Terminal 1:**
```bash
cd /Users/cohan/Documents/campsite-search-resevation
./start-backend.sh
```

**Terminal 2:**
```bash
cd /Users/cohan/Documents/campsite-search-resevation
./start-frontend.sh
```

That's it! 🏕️
