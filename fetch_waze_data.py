"""
Waze Data Fetcher
Fetches incident data from Waze Partner Hub API and saves it for visualization.
"""

import requests
import json
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
    

