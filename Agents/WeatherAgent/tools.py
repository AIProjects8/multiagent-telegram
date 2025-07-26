import requests
from typing import Dict, Any
from config import Config

def get_weather(lat: float, lon: float) -> Dict[str, Any]:
    config = Config.from_env()
    
    url = f"https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "exclude": "current,minutely,daily,alerts",
        "units": "metric",
        "appid": config.open_weather_map_api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch weather data: {str(e)}"}