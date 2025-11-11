from .date_converter import convert_dates
from .contextual_time_converter import convert_contextual_time
from .standalone_time_converter import convert_standalone_time

def convert(text: str) -> str:

    result = convert_dates(text)
    result = convert_contextual_time(result)
    result = convert_standalone_time(result)
    
    return result
