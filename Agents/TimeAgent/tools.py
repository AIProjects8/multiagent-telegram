from datetime import datetime, timedelta
import pytz
from suntime import Sun
from timezonefinder import TimezoneFinder

def get_sunrise(lat: float, lon: float, city_name: str = None, current_time: datetime = datetime.now()) -> dict:
    """Get sunrise time for a location"""
    try:
        sun = Sun(lat, lon)
        
        # Get timezone for the specific location
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=lat, lng=lon)
        
        if timezone_str:
            location_tz = pytz.timezone(timezone_str)
        else:
            # Fallback to UTC if timezone cannot be determined
            location_tz = pytz.UTC
        
        current_time_local = current_time.astimezone(location_tz)
        
        today_sunrise = sun.get_sunrise_time(current_time)
        
        tomorrow = current_time + timedelta(days=1)
        tomorrow_sunrise = sun.get_sunrise_time(tomorrow)
        
        if today_sunrise and tomorrow_sunrise:
            today_sunrise_local = today_sunrise.astimezone(location_tz)
            tomorrow_sunrise_local = tomorrow_sunrise.astimezone(location_tz)
            
            today_passed = today_sunrise_local < current_time_local
            
            return {
                "success": True,
                "city_name": city_name,
                "today_time": today_sunrise_local.strftime("%H:%M"),
                "tomorrow_time": tomorrow_sunrise_local.strftime("%H:%M"),
                "today_passed": today_passed
            }
        else:
            return {"success": False, "error": "Failed to calculate sunrise time"}
            
    except Exception as e:
        return {"success": False, "error": f"Error calculating sunrise time: {str(e)}"}

def get_sunset(lat: float, lon: float, city_name: str = None, current_time: datetime = datetime.now()) -> dict:
    """Get sunset time for a location"""
    try:
        sun = Sun(lat, lon)
        
        # Get timezone for the specific location
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=lat, lng=lon)
        
        if timezone_str:
            location_tz = pytz.timezone(timezone_str)
        else:
            # Fallback to UTC if timezone cannot be determined
            location_tz = pytz.UTC
        
        current_time_local = current_time.astimezone(location_tz)
        
        today_sunset = sun.get_sunset_time(current_time)
        
        tomorrow = current_time + timedelta(days=1)
        tomorrow_sunset = sun.get_sunset_time(tomorrow)
        
        if today_sunset and tomorrow_sunset:
            today_sunset_local = today_sunset.astimezone(location_tz)
            tomorrow_sunset_local = tomorrow_sunset.astimezone(location_tz)
            
            today_passed = today_sunset_local < current_time_local
            
            return {
                "success": True,
                "city_name": city_name,
                "today_time": today_sunset_local.strftime("%H:%M"),
                "tomorrow_time": tomorrow_sunset_local.strftime("%H:%M"),
                "today_passed": today_passed
            }
        else:
            return {"success": False, "error": "Failed to calculate sunset time"}
            
    except Exception as e:
        return {"success": False, "error": f"Error calculating sunset time: {str(e)}"}
