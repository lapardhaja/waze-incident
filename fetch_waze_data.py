"""
Waze Data Fetcher
Fetches incident data from Waze Partner Hub API and saves it for visualization.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import os


class WazeDataFetcher:
    def __init__(self, api_url: str):
        """
        Initialize the Waze Data Fetcher.
        
        Args:
            api_url: The Waze Partner Hub API endpoint URL
        """
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_data(self) -> Optional[Dict]:
        """
        Fetch data from the Waze API.
        
        Returns:
            Dictionary containing the API response, or None if request fails
        """
        try:
            response = self.session.get(self.api_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    
    def extract_incidents(self, data: Dict) -> List[Dict]:
        """
        Extract incident data from the Waze API response.
        
        Args:
            data: The JSON response from the Waze API
            
        Returns:
            List of incident dictionaries with lat, lng, type, and other relevant info
        """
        incidents = []
        
        # Waze API typically returns data in a structure like:
        # { "alerts": [...], "jams": [...] }
        # Incidents are usually in the "alerts" array
        # Handle different possible response structures
        
        alerts = []
        
        # Try different possible structures
        if isinstance(data, dict):
            if 'alerts' in data:
                alerts = data['alerts']
            elif 'data' in data and isinstance(data['data'], dict) and 'alerts' in data['data']:
                alerts = data['data']['alerts']
            elif 'items' in data:
                # Sometimes data might be directly in items
                alerts = data['items']
        elif isinstance(data, list):
            # If the response is directly a list
            alerts = data
        
        for alert in alerts:
            if not isinstance(alert, dict):
                continue
                
            # Try different location formats
            lat = None
            lng = None
            
            # Format 1: location: { x: lng, y: lat }
            if 'location' in alert:
                loc = alert['location']
                if isinstance(loc, dict):
                    lat = loc.get('y') or loc.get('latitude') or loc.get('lat')
                    lng = loc.get('x') or loc.get('longitude') or loc.get('lng') or loc.get('lon')
            
            # Format 2: Direct lat/lng fields
            if not lat or not lng:
                lat = alert.get('lat') or alert.get('latitude') or alert.get('y')
                lng = alert.get('lng') or alert.get('longitude') or alert.get('lon') or alert.get('x')
            
            # Format 3: coordinates array [lng, lat]
            if not lat or not lng:
                if 'coordinates' in alert:
                    coords = alert['coordinates']
                    if isinstance(coords, list) and len(coords) >= 2:
                        lng, lat = coords[0], coords[1]
            
            # Skip if no valid coordinates
            if not lat or not lng:
                continue
            
            # Try to convert to float
            try:
                lat = float(lat)
                lng = float(lng)
            except (ValueError, TypeError):
                continue
            
            # Build incident object
            incident = {
                'lat': lat,
                'lng': lng,
                'type': alert.get('type', alert.get('alertType', 'unknown')),
                'subtype': alert.get('subtype', alert.get('alertSubtype', '')),
                'street': alert.get('street', ''),
                'city': alert.get('city', ''),
                'country': alert.get('country', ''),
                'reliability': alert.get('reliability', alert.get('confidence', 0)),
                'reportRating': alert.get('reportRating', alert.get('report_rating', 0)),
                'pubMillis': alert.get('pubMillis', alert.get('pub_millis', alert.get('timestamp', 0))),
            }
            
            # Add timestamp if we have pubMillis
            if incident['pubMillis']:
                try:
                    # Handle both milliseconds and seconds timestamps
                    millis = incident['pubMillis']
                    if millis < 1e10:  # Likely in seconds
                        millis = millis * 1000
                    incident['timestamp'] = datetime.fromtimestamp(millis / 1000).isoformat()
                except (ValueError, OSError):
                    incident['timestamp'] = None
            else:
                incident['timestamp'] = None
            
            # Add any additional fields that might be useful
            for key in ['description', 'uuid', 'magvar', 'roadType', 'reportBy']:
                if key in alert:
                    incident[key] = alert[key]
            
            incidents.append(incident)
        
        return incidents
    
    def save_incidents(self, incidents: List[Dict], filename: str = 'incidents.json'):
        """
        Save incidents to a JSON file.
        
        Args:
            incidents: List of incident dictionaries
            filename: Output filename
        """
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        
        with open(filepath, 'w') as f:
            json.dump(incidents, f, indent=2)
        
        print(f"Saved {len(incidents)} incidents to {filepath}")
    
    def fetch_and_save(self, filename: Optional[str] = None):
        """
        Fetch data from API and save incidents to file.
        
        Args:
            filename: Optional custom filename (defaults to timestamp-based name)
        """
        print("Fetching Waze data...")
        data = self.fetch_data()
        
        if data is None:
            print("Failed to fetch data from API")
            return None
        
        incidents = self.extract_incidents(data)
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'incidents_{timestamp}.json'
        
        self.save_incidents(incidents, filename)
        
        # Also save as latest for easy access
        if filename != 'incidents_latest.json':
            self.save_incidents(incidents, 'incidents_latest.json')
        
        return incidents


def main():
    """Main function to run the fetcher."""
    # Load API URL from config or use default
    config_file = 'config.json'
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            api_url = config.get('waze_api_url')
    else:
        # Default API URL (user should update this)
        api_url = "https://www.waze.com/partnerhub-api/partners/11533082963/waze-feeds/693756bf-6eb5-409b-bfe4-c5472f4e3a73?format=1"
        print(f"Using default API URL. Update config.json to customize.")
    
    if not api_url:
        print("Error: No API URL configured. Please set waze_api_url in config.json")
        return
    
    fetcher = WazeDataFetcher(api_url)
    incidents = fetcher.fetch_and_save()
    
    if incidents:
        print(f"\nSummary:")
        print(f"Total incidents: {len(incidents)}")
        
        # Count by type
        type_counts = {}
        for incident in incidents:
            incident_type = incident.get('type', 'unknown')
            type_counts[incident_type] = type_counts.get(incident_type, 0) + 1
        
        print("\nIncidents by type:")
        for incident_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {incident_type}: {count}")


if __name__ == '__main__':
    main()

