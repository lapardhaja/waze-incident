"""
Waze Incidents Server
Runs a web server and continuously fetches/accumulates Waze incident data.
"""

import http.server
import socketserver
import threading
import time
import json
import os
import webbrowser
from datetime import datetime
from pathlib import Path

from fetch_waze_data import WazeDataFetcher
from accumulate_incidents import IncidentAccumulator


class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with CORS support for local development."""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Suppress HTTP request logs to keep console clean
        pass


def run_server(port=None):
    """Run the HTTP server."""
    # Support PORT environment variable for cloud platforms
    if port is None:
        port = int(os.environ.get('PORT', 8000))
    
    handler = CORSRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        # Don't try to open browser in cloud environments
        if not os.environ.get('RAILWAY_ENVIRONMENT') and not os.environ.get('RENDER'):
            print(f"Server running at http://localhost:{port}/heatmap.html")
        else:
            print(f"Server running on port {port}")
        httpd.serve_forever()


def run_fetcher(api_url: str, interval: int, accumulator: IncidentAccumulator, fetcher: WazeDataFetcher):
    """Continuously fetch and accumulate incidents."""
    while True:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{timestamp}] Fetching incidents...")
            
            data = fetcher.fetch_data()
            if data is None:
                print("  Failed to fetch data")
                time.sleep(interval)
                continue
            
            new_incidents = fetcher.extract_incidents(data)
            result = accumulator.add_incidents(new_incidents)
            
            print(f"  Fetched: {len(new_incidents)} | New: {result['new']} | Duplicates: {result['duplicates']} | Total: {result['total']}")
            
            accumulator.save_master()
            
        except Exception as e:
            print(f"  Error: {e}")
        
        time.sleep(interval)


def main():
    """Main entry point."""
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Load configuration - support environment variables for cloud deployment
    api_url = os.environ.get('WAZE_API_URL')
    interval = int(os.environ.get('UPDATE_INTERVAL_SECONDS', 120))
    
    # Fallback to config.json if env vars not set
    if not api_url:
        config_file = 'config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                api_url = config.get('waze_api_url')
                interval = config.get('update_interval_seconds', 120)
        else:
            print("Error: config.json not found and WAZE_API_URL not set")
            return
    
    if not api_url:
        print("Error: No API URL configured")
        return
    
    # Initialize components
    accumulator = IncidentAccumulator()
    fetcher = WazeDataFetcher(api_url)
    
    print("=" * 50)
    print("Waze Incidents Heatmap Server")
    print("=" * 50)
    print(f"Fetch interval: {interval} seconds")
    print(f"Existing incidents: {len(accumulator.master_incidents)}")
    print("=" * 50)
    
    # Start fetcher thread
    fetcher_thread = threading.Thread(
        target=run_fetcher,
        args=(api_url, interval, accumulator, fetcher),
        daemon=True
    )
    fetcher_thread.start()
    
    # Do initial fetch immediately
    print("\nPerforming initial fetch...")
    data = fetcher.fetch_data()
    if data:
        new_incidents = fetcher.extract_incidents(data)
        result = accumulator.add_incidents(new_incidents)
        print(f"  Fetched: {len(new_incidents)} | New: {result['new']} | Total: {result['total']}")
        accumulator.save_master()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 8000))
    
    # Open browser (only in local environment)
    if not os.environ.get('RAILWAY_ENVIRONMENT') and not os.environ.get('RENDER'):
        url = f"http://localhost:{port}/heatmap.html"
        print(f"\nOpening browser: {url}")
        try:
            webbrowser.open(url)
        except:
            print(f"Please open {url} manually")
        print("\nServer is running. Press Ctrl+C to stop.\n")
    else:
        print(f"\nServer is running in cloud environment on port {port}.\n")
    
    # Run server (blocking)
    try:
        run_server(port)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        accumulator.save_master()
        print("Data saved. Goodbye!")


if __name__ == '__main__':
    main()

