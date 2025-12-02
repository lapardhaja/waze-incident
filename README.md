# Waze Incidents Heatmap

A real-time web application that visualizes Waze incident data as an interactive heatmap with automatic data collection and deduplication.

## Features

- **Automatic Data Collection**: Continuously fetches incidents from Waze Partner Hub API
- **Smart Deduplication**: Never double-counts incidents using UUID or location+time matching
- **Interactive Heatmap**: Visualize incident hotspots with density visualization
- **Individual Markers**: Zoom in (level 15+) to see individual incidents with details
- **Time Filtering**: Filter by last hour, 6 hours, 24 hours, 7 days, or custom date range
- **Type Filtering**: Filter by incident type (Accident, Hazard, Jam, etc.)
- **Auto-Refresh**: Heatmap updates automatically as new data arrives
- **Cloud-Ready**: Supports deployment to Render, Heroku, and other platforms

## Quick Start

### Prerequisites

- Python 3.11+
- Waze Partner Hub API access

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "Waze Incident"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the API URL:**
   
   Create or edit `config.json`:
   ```json
   {
     "waze_api_url": "YOUR_WAZE_API_URL",
     "update_interval_seconds": 120
   }
   ```
   
   Or set environment variables:
   ```bash
   export WAZE_API_URL="YOUR_WAZE_API_URL"
   export UPDATE_INTERVAL_SECONDS=120
   ```

4. **Run the server:**
   ```bash
   python run.py
   ```

The browser will open automatically showing the heatmap at `http://localhost:8000/heatmap.html`. The server continuously fetches new incidents every 2 minutes (configurable) and deduplicates them.

## Project Structure

```
.
├── run.py                    # Main server (runs web server + data fetcher)
├── fetch_waze_data.py        # Waze API data fetcher
├── accumulate_incidents.py   # Incident deduplication logic
├── heatmap.html              # Interactive map visualization
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
├── Procfile                  # Heroku deployment config
├── render.yaml               # Render deployment config
├── runtime.txt               # Python version specification
└── data/                     # Stored incident data
    ├── incidents_master.json # Master database (all unique incidents)
    └── incidents_latest.json # Latest snapshot (for heatmap)
```

## How It Works

1. **Server starts** → Opens browser to heatmap and initializes data fetcher
2. **Fetcher runs** → Gets incidents from Waze API at configured intervals
3. **Deduplication** → Only new unique incidents are added to master database
4. **Heatmap updates** → Click refresh or enable auto-refresh to see latest data

### Deduplication Strategy

The system uses a multi-tier approach to identify unique incidents:

1. **Primary**: UUID (if available from Waze API)
2. **Secondary**: Location (rounded to ~1m precision) + Type + Timestamp
3. **Fallback**: Location + Type + Street name

## Configuration

### Local Development

Edit `config.json`:
```json
{
  "waze_api_url": "https://www.waze.com/partnerhub-api/...",
  "update_interval_seconds": 120
}
```

### Environment Variables (Cloud Deployment)

- `WAZE_API_URL` - Your Waze Partner Hub API endpoint
- `UPDATE_INTERVAL_SECONDS` - Fetch interval in seconds (default: 120)
- `GITHUB_TOKEN` - GitHub personal access token for Gist storage (optional, falls back to file storage)
- `GIST_ID` - GitHub Gist ID for storing incidents (optional, requires GITHUB_TOKEN)
- `PORT` - Server port (default: 8000, auto-set by cloud platforms)
- `RENDER` - Set automatically by Render.com (disables browser opening)

## Deployment

### Render.com

1. **Connect your GitHub repository** to Render
2. **Create a new Web Service**
3. **Configure:**
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
4. **Add Environment Variables:**
   - `WAZE_API_URL`: Your Waze API URL
   - `UPDATE_INTERVAL_SECONDS`: `120` (optional)
5. **Deploy!**

The `render.yaml` file is included for automated configuration.

### Heroku

1. **Install Heroku CLI** and login
2. **Create app:**
   ```bash
   heroku create your-app-name
   ```
3. **Set environment variables:**
   ```bash
   heroku config:set WAZE_API_URL="YOUR_API_URL"
   heroku config:set UPDATE_INTERVAL_SECONDS=120
   ```
4. **Deploy:**
   ```bash
   git push heroku main
   ```

The `Procfile` is included for Heroku deployment.

## Viewing Modes

- **Zoomed out**: Heatmap shows incident density (hotspots)
- **Zoomed in (level 15+)**: Individual markers with click-for-details

## Data Storage

- **`data/incidents_master.json`**: Complete database of all unique incidents (grows over time)
- **`data/incidents_latest.json`**: Latest snapshot used by the heatmap (same data, regenerated on each save)

### ⚠️ Important: Render.com Data Persistence

**Render's filesystem is ephemeral** - data files are lost when the service restarts or redeploys. This means:

- ✅ Data **will update** while the app is running
- ❌ Data **will be lost** on restart/redeploy (starts fresh each time)

**Solution: Use GitHub Gist (FREE & Simple)**

The app now supports GitHub Gist for persistent storage. It's super simple - just 2 steps:

1. **Create a GitHub Personal Access Token:**
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Name it: `waze-incidents`
   - Check only: `gist` (create gists)
   - Click "Generate token" and **copy it** (you won't see it again!)

2. **Create a Gist and get its ID:**
   - Go to [gist.github.com](https://gist.github.com)
   - Create a new gist (make it **secret** or public, your choice)
   - Name the file: `incidents.json`
   - Content: `[]` (empty array)
   - Click "Create secret gist" or "Create public gist"
   - Copy the Gist ID from the URL (the long string after `/gist/`)

3. **Set environment variables on Render:**
   - Key: `GITHUB_TOKEN` → Value: Your personal access token
   - Key: `GIST_ID` → Value: Your gist ID

**That's it!** The app will automatically:
- Use GitHub Gist if both variables are set (persistent storage)
- Fall back to file storage if not set (local development)

**Example Gist URL:** `https://gist.github.com/username/abc123def456...`
**Gist ID:** `abc123def456...` (the part after the last slash)

## Troubleshooting

- **"Error: config.json not found"**: Create `config.json` or set `WAZE_API_URL` environment variable
- **"Failed to fetch data"**: Check your API URL and network connection
- **Port already in use**: Change the port via `PORT` environment variable
- **No incidents showing**: Check API URL is correct and returns data in expected format

## License

For use with Waze Partner Hub data. Ensure compliance with Waze's terms of service.
