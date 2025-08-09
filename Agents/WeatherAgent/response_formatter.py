from typing import Dict, Any
from datetime import datetime
import pytz
from Agents.WeatherAgent.constants import day_names, month_names
from suntime import Sun

def format_weather_response(weather_data: Dict[str, Any], lat: float, lon: float, city_name: str) -> str:
    if "error" in weather_data:
        return f"Błąd: {weather_data['error']}"
    
    if "hourly" not in weather_data or not weather_data["hourly"]:
        return "Brak dostępnych danych pogodowych."
    
    hourly_forecast = weather_data["hourly"][:24]
    
    temps = [hour.get("temp") for hour in hourly_forecast if hour.get("temp") is not None]
    min_temp = min(temps) if temps else None
    max_temp = max(temps) if temps else None
    
    now = datetime.now()

    day_name = day_names[now.weekday()]
    day = now.day

    month_name = month_names[now.month]
    
    response = f"Prognoza pogody dla miejscowości {city_name} na {day_name} {day} {month_name}. "
    
    if min_temp is not None and max_temp is not None:
        min_temp_rounded = round(min_temp)
        max_temp_rounded = round(max_temp)
        response += f"Temperatura będzie się wahać od {min_temp_rounded} do {max_temp_rounded} stopni Celsjusza. "
    
    rain_hours = []
    snow_hours = []
    fog_hours = []
    strong_wind_hours = []
    cloudy_hours = []
    clear_hours = []
    
    for i, hour_data in enumerate(hourly_forecast):
        dt_timestamp = hour_data.get("dt", 0)
        dt_utc = datetime.fromtimestamp(dt_timestamp, tz=pytz.UTC)
        poland_tz = pytz.timezone('Europe/Warsaw')
        dt_poland = dt_utc.astimezone(poland_tz)
        hour = dt_poland.hour
        
        weather_main = hour_data.get("weather", [{}])[0].get("main", "").lower()
        weather_desc = hour_data.get("weather", [{}])[0].get("description", "").lower()
        wind_speed = hour_data.get("wind_speed", 0)
        pop = hour_data.get("pop", 0)
        clouds = hour_data.get("clouds", 0)
        
        if "rain" in weather_main or "drizzle" in weather_main or pop > 0.3:
            rain_hours.append(hour)
        
        if "snow" in weather_main:
            snow_hours.append(hour)
        
        if "fog" in weather_desc or "mist" in weather_desc:
            fog_hours.append(hour)
        
        if wind_speed > 20:
            strong_wind_hours.append(hour)
        
        if clouds > 80:
            cloudy_hours.append(hour)
        elif clouds < 20:
            clear_hours.append(hour)
    
    if rain_hours:
        rain_times = format_hour_ranges(rain_hours)
        response += f"Opady deszczu przewidywane są {rain_times}. "
    
    if snow_hours:
        snow_times = format_hour_ranges(snow_hours)
        response += f"Śnieg może padać {snow_times}. "
    
    if fog_hours:
        fog_times = format_hour_ranges(fog_hours)
        response += f"Mgła może wystąpić {fog_times}. "
    
    if strong_wind_hours:
        wind_times = format_hour_ranges(strong_wind_hours)
        response += f"Silny wiatr przewidywany jest {wind_times}. "
    
    if cloudy_hours:
        cloudy_times = format_hour_ranges(cloudy_hours)
        response += f"Zachmurzenie duże {cloudy_times}. "
    
    if clear_hours:
        clear_times = format_hour_ranges(clear_hours)
        response += f"Bezchmurne niebo {clear_times}. "
    
    if not any([rain_hours, snow_hours]):
        response += "Nie przewiduje się opadów. "
    
    return response

def format_hour_ranges(hours: list) -> str:
    if not hours:
        return ""
    
    def format_hour(hour):
        return f"{hour:02d}:00"
    
    if len(hours) == 1:
        return f"o godzinie {format_hour(hours[0])}"
    
    ranges = []
    start = hours[0]
    end = hours[0]
    
    for i in range(1, len(hours)):
        if hours[i] == end + 1:
            end = hours[i]
        else:
            if start == end:
                ranges.append(f"o godzinie {format_hour(start)}")
            else:
                ranges.append(f"od {format_hour(start)} do {format_hour(end)}")
            start = end = hours[i]
    
    if start == end:
        ranges.append(f"o godzinie {format_hour(start)}")
    else:
        ranges.append(f"od {format_hour(start)} do {format_hour(end)}")
    
    if len(ranges) == 1:
        return ranges[0]
    elif len(ranges) == 2:
        return f"{ranges[0]} i {ranges[1]}"
    else:
        return f"{', '.join(ranges[:-1])} i {ranges[-1]}"
