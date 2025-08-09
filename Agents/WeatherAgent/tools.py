import requests
from config import Config

def get_weather(lat: float, lon: float) -> dict:
    config = Config.from_env()
    
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": config.open_weather_map_api_key,
        "units": "metric",
        "exclude": "minutely,daily,alerts"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}