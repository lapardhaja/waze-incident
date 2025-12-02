"""
Accumulate Waze incidents over time, ensuring no duplicates.
Maintains a master incidents database that grows over time.
"""

import json
import os
from datetime import datetime
from fetch_waze_data import WazeDataFetcher
from typing import List, Dict, Set


class IncidentAccumulator:
    def __init__(self, master_file: str = 'data/incidents_master.json'):
        """
        Initialize the incident accumulator.
        
        Args:
            master_file: Path to the master incidents file
        """
        self.master_file = master_file
        self.master_incidents: List[Dict] = []
        self.load_master()
    
    def load_master(self):
        """Load existing master incidents file."""
        if os.path.exists(self.master_file):
            try:
                with open(self.master_file, 'r') as f:
                    self.master_incidents = json.load(f)
                print(f"Loaded {len(self.master_incidents)} existing incidents from master file")
            except Exception as e:
                print(f"Error loading master file: {e}")
                self.master_incidents = []
        else:
            self.master_incidents = []
            os.makedirs(os.path.dirname(self.master_file) if os.path.dirname(self.master_file) else '.', exist_ok=True)
    
    def get_incident_key(self, incident: Dict) -> str:
        """
        Generate a unique key for an incident to detect duplicates.
        Uses UUID if available, otherwise uses a combination of fields.
        
        Args:
            incident: Incident dictionary
            
        Returns:
            Unique string key for the incident
        """
        # Primary: Use UUID if available (most reliable)
        if 'uuid' in incident and incident['uuid']:
            return f"uuid:{incident['uuid']}"
        
        # Secondary: Use combination of location, type, and timestamp
        # Round coordinates to 5 decimal places (~1 meter precision) to handle slight variations
        lat = round(float(incident.get('lat', 0)), 5)
        lng = round(float(incident.get('lng', 0)), 5)
        incident_type = incident.get('type', 'unknown')
        pub_millis = incident.get('pubMillis', 0)
        
        # If we have a timestamp, use it for uniqueness
        if pub_millis:
            return f"loc:{lat}:{lng}:type:{incident_type}:time:{pub_millis}"
        
        # Fallback: location + type + street (less reliable but better than nothing)
        street = incident.get('street', '')
        return f"loc:{lat}:{lng}:type:{incident_type}:street:{street}"
    
    def add_incidents(self, new_incidents: List[Dict]) -> Dict:
        """
        Add new incidents to the master list, avoiding duplicates.
        
        Args:
            new_incidents: List of new incident dictionaries
            
        Returns:
            Dictionary with statistics about added incidents
        """
        if not new_incidents:
            return {'total': len(self.master_incidents), 'new': 0, 'duplicates': 0}
        
        # Get existing keys
        existing_keys: Set[str] = {self.get_incident_key(inc) for inc in self.master_incidents}
        
        # Track statistics
        new_count = 0
        duplicate_count = 0
        
        # Add new incidents that aren't duplicates
        for incident in new_incidents:
            key = self.get_incident_key(incident)
            if key not in existing_keys:
                self.master_incidents.append(incident)
                existing_keys.add(key)
                new_count += 1
            else:
                duplicate_count += 1
        
        return {
            'total': len(self.master_incidents),
            'new': new_count,
            'duplicates': duplicate_count
        }
    
    def save_master(self):
        """Save the master incidents list to file."""
        os.makedirs(os.path.dirname(self.master_file) if os.path.dirname(self.master_file) else '.', exist_ok=True)
        
        with open(self.master_file, 'w') as f:
            json.dump(self.master_incidents, f, indent=2)
        
        # Also save as latest for the heatmap
        latest_file = 'data/incidents_latest.json'
        with open(latest_file, 'w') as f:
            json.dump(self.master_incidents, f, indent=2)
        
        print(f"Saved {len(self.master_incidents)} incidents to master file")
    
    def get_statistics(self) -> Dict:
        """Get statistics about accumulated incidents."""
        stats = {
            'total': len(self.master_incidents),
            'by_type': {},
            'by_city': {},
            'date_range': None
        }
        
        if not self.master_incidents:
            return stats
        
        # Count by type
        for incident in self.master_incidents:
            incident_type = incident.get('type', 'unknown')
            stats['by_type'][incident_type] = stats['by_type'].get(incident_type, 0) + 1
            
            city = incident.get('city', 'unknown')
            stats['by_city'][city] = stats['by_city'].get(city, 0) + 1
        
        # Date range
        timestamps = [inc.get('pubMillis', 0) for inc in self.master_incidents if inc.get('pubMillis')]
        if timestamps:
            min_time = min(timestamps)
            max_time = max(timestamps)
            stats['date_range'] = {
                'earliest': datetime.fromtimestamp(min_time / 1000).isoformat(),
                'latest': datetime.fromtimestamp(max_time / 1000).isoformat()
            }
        
        return stats


def main():
    """Main function to fetch and accumulate incidents."""
    import time
    
    # Load configuration
    config_file = 'config.json'
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            api_url = config.get('waze_api_url')
            interval = config.get('update_interval_seconds', 120)
    else:
        api_url = "https://www.waze.com/partnerhub-api/partners/11533082963/waze-feeds/693756bf-6eb5-409b-bfe4-c5472f4e3a73?format=1"
        interval = 120
        print(f"Using default settings. Update config.json to customize.")
    
    if not api_url:
        print("Error: No API URL configured. Please set waze_api_url in config.json")
        return
    
    # Initialize accumulator
    accumulator = IncidentAccumulator()
    
    # Initialize fetcher
    fetcher = WazeDataFetcher(api_url)
    
    print(f"Starting continuous incident accumulation (interval: {interval} seconds)")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching new incidents...")
            
            # Fetch new data
            data = fetcher.fetch_data()
            if data is None:
                print("Failed to fetch data from API\n")
                time.sleep(interval)
                continue
            
            # Extract incidents
            new_incidents = fetcher.extract_incidents(data)
            print(f"Fetched {len(new_incidents)} incidents from API")
            
            # Add to accumulator
            result = accumulator.add_incidents(new_incidents)
            
            # Print statistics
            print(f"  - New incidents added: {result['new']}")
            print(f"  - Duplicates skipped: {result['duplicates']}")
            print(f"  - Total incidents in database: {result['total']}")
            
            # Save master file
            accumulator.save_master()
            
            # Show overall statistics
            stats = accumulator.get_statistics()
            print(f"\nStatistics:")
            print(f"  - Total unique incidents: {stats['total']}")
            if stats['by_type']:
                print(f"  - By type: {', '.join([f'{k}: {v}' for k, v in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True)])}")
            if stats['date_range']:
                print(f"  - Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
            
            print(f"\nWaiting {interval} seconds until next fetch...\n")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
        print("Saving final state...")
        accumulator.save_master()
        stats = accumulator.get_statistics()
        print(f"\nFinal statistics:")
        print(f"  - Total unique incidents: {stats['total']}")
        print("Exiting...")


if __name__ == '__main__':
    main()

