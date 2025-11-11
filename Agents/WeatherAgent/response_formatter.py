from typing import Dict, Any, Callable
from datetime import datetime
import pytz

from Modules.TranslationTools.pl.constants import day_names

def format_weather_response(weather_data: Dict[str, Any], city_name: str, translate_func: Callable[[str], str]) -> str:
    if "error" in weather_data:
        return f"Error: {weather_data['error']}"
    
    if "hourly" not in weather_data or not weather_data["hourly"]:
        return translate_func("No weather data available.")
    
    hourly_forecast = weather_data["hourly"][:24]
    
    temps = [hour.get("temp") for hour in hourly_forecast if hour.get("temp") is not None]
    min_temp = min(temps) if temps else None
    max_temp = max(temps) if temps else None
    
    now = datetime.now()

    day_name = day_names[now.weekday()]
    day = now.day
    month = now.month
    year = now.year

    response = translate_func("Weather forecast for {city} on {day} {date}. ").format(city=city_name, day=day_name, date=f"{day:02d}.{month:02d}.{year}")
    
    if min_temp is not None and max_temp is not None:
        min_temp_rounded = round(min_temp)
        max_temp_rounded = round(max_temp)
        response += translate_func("Temperature will range from {min_temp} to {max_temp} degrees Celsius. ").format(min_temp=min_temp_rounded, max_temp=max_temp_rounded)
    
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
        rain_times = format_hour_ranges(rain_hours, translate_func)
        response += translate_func("Rain is expected {times}. ").format(times=rain_times)
    
    if snow_hours:
        snow_times = format_hour_ranges(snow_hours, translate_func)
        response += translate_func("Snow may fall {times}. ").format(times=snow_times)
    
    if fog_hours:
        fog_times = format_hour_ranges(fog_hours, translate_func)
        response += translate_func("Fog may occur {times}. ").format(times=fog_times)
    
    if strong_wind_hours:
        wind_times = format_hour_ranges(strong_wind_hours, translate_func)
        response += translate_func("Strong wind is expected {times}. ").format(times=wind_times)
    
    if cloudy_hours:
        cloudy_times = format_hour_ranges(cloudy_hours, translate_func)
        response += translate_func("Heavy cloud cover {times}. ").format(times=cloudy_times)
    
    if clear_hours:
        clear_times = format_hour_ranges(clear_hours, translate_func)
        response += translate_func("Clear sky {times}. ").format(times=clear_times)
    
    if not any([rain_hours, snow_hours]):
        response += translate_func("No precipitation is expected. ")
    
    return response

def format_hour_ranges(hours: list, _: Callable[[str], str]) -> str:
    if not hours:
        return ""
    
    def format_hour(hour):
        return f"{hour:02d}:00"
    
    if len(hours) == 1:
        return _("at {hour}").format(hour=format_hour(hours[0]))
    
    ranges = []
    start = hours[0]
    end = hours[0]
    
    for i in range(1, len(hours)):
        if hours[i] == end + 1:
            end = hours[i]
        else:
            if start == end:
                ranges.append(_("at {hour}").format(hour=format_hour(start)))
            else:
                ranges.append(_("from {start_hour} to {end_hour}").format(start_hour=format_hour(start), end_hour=format_hour(end)))
            start = end = hours[i]
    
    if start == end:
        ranges.append(_("at {hour}").format(hour=format_hour(start)))
    else:
        ranges.append(_("from {start_hour} to {end_hour}").format(start_hour=format_hour(start), end_hour=format_hour(end)))
    
    if len(ranges) == 1:
        return ranges[0]
    elif len(ranges) == 2:
        return f"{ranges[0]}{_(' and ')}{ranges[1]}"
    else:
        return f"{', '.join(ranges[:-1])}{_(' and ')}{ranges[-1]}"
