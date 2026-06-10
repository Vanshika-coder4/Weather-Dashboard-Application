# weather_api.py
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import time
from typing import Optional, Dict, Any

class WeatherAPI:
    """Handles all weather API interactions"""
    
    def __init__(self, api_key: str, base_url: str = "http://api.openweathermap.org/data/2.5"):
        self.api_key = api_key
        self.base_url = base_url
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = 600  # 10 minutes in seconds
        
    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if valid"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            # Check if cache is still valid
            cache_time = cache_file.stat().st_mtime
            if time.time() - cache_time < self.cache_duration:
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except:
                    pass
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save data to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            params['appid'] = self.api_key
            params['units'] = 'metric'  # Use metric units
            
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("Error: Invalid API key")
            elif response.status_code == 404:
                print("Error: City not found")
            elif response.status_code == 429:
                print("Error: API rate limit exceeded")
            else:
                print(f"Error: API request failed with status {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("Error: Request timed out")
        except requests.exceptions.ConnectionError:
            print("Error: Network connection error")
        except Exception as e:
            print(f"Error: {e}")
            
        return None
    
    def get_current_weather(self, city: str, country_code: str = None) -> Optional[Dict]:
        """Get current weather for a city"""
        cache_key = f"current_{city}_{country_code}" if country_code else f"current_{city}"
        
        # Check cache first
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        # Build query
        query = city
        if country_code:
            query = f"{city},{country_code}"
        
        # Make API request
        params = {'q': query}
        data = self._make_request("weather", params)
        
        if data:
            self._save_to_cache(cache_key, data)
            
        return data