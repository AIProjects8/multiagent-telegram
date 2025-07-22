def validate_hour_format(time_str):
    if not isinstance(time_str, str):
        return None
    parts = time_str.split(":")
    if len(parts) != 2:
        return None
    hour, minute = parts
    if not (hour.isdigit() and minute.isdigit()):
        return None
    hour = int(hour)
    minute = int(minute)
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return f"{hour:02d}:{minute:02d}"
    return None
