# Waze Incidents Heatmap

Visualize Waze incident data as an interactive heatmap with automatic data collection.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python run.py
   ```

That's it! The browser will open automatically showing the heatmap. The server continuously fetches new incidents every 2 minutes and deduplicates them.

## Features

- **Automatic Data Collection**: Fetches incidents every 2 minutes
- **Deduplication**: Never double-counts incidents (uses UUID or location+time)
- **Interactive Heatmap**: See incident hotspots at a glance
- **Individual Markers**: Zoom in (level 15+) to see individual incidents with details
- **Time Filtering**: Filter by last hour, 6 hours, 24 hours, 7 days, or custom date range
- **Type Filtering**: Filter by incident type (Accident, Hazard, Jam, etc.)
- **Auto-Refresh**: Heatmap updates automatically as new data arrives

## Configuration

Edit `config.json` to customize:

```json
{
  "waze_api_url": "YOUR_WAZE_API_URL",
  "update_interval_seconds": 120
}
```

## Files

- `run.py` - Main server (runs web server + data fetcher)
- `heatmap.html` - Interactive map visualization
- `fetch_waze_data.py` - Waze API data fetcher
- `accumulate_incidents.py` - Incident deduplication logic
- `config.json` - Configuration
- `data/` - Stored incident data

## How It Works

1. **Server starts** → Opens browser to heatmap
2. **Fetcher runs** → Gets incidents from Waze API every 2 minutes
3. **Deduplication** → Only new unique incidents are added
4. **Heatmap updates** → Click refresh or enable auto-refresh

## Viewing Modes

- **Zoomed out**: Heatmap shows incident density (hotspots)
- **Zoomed in (15+)**: Individual markers with click-for-details

## License

For use with Waze Partner Hub data. Ensure compliance with Waze's terms of service.
