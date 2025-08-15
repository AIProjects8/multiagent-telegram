import re

def convert_contextual_time(text: str) -> str:
    """
    Convert hour formats in weather messages from numeric to Polish text format.
    
    Converts patterns like:
    - "od godziny XX:XX" -> "od godziny [polish_hour] [polish_minutes]"
    - "od XX:XX" -> "od [polish_hour] [polish_minutes]"
    - "do godziny XX:XX" -> "do godziny [polish_hour] [polish_minutes]"
    - "do XX:XX" -> "do [polish_hour] [polish_minutes]"
    - "o godzinie XX:XX" -> "o godzinie [polish_hour] [polish_minutes]"
    - "o XX:XX" -> "o [polish_hour] [polish_minutes]"
    
    Handles:
    - Full hours (12:00) -> dwunastej
    - Minutes 1-9 (12:03) -> dwunastej zero trzy
    - Minutes 10+ (12:39) -> dwunastej trzydzieści dziewięć
    
    Special case for midnight (00:00):
    - "od godziny 00:00" -> "od północy"
    - "o godzinie 00:00" -> "o północy"
    - "do godziny 00:00" -> "do północy"
    """
    
    # Polish hour names in dopełniacz (genitive case)
    polish_hours = {
        "00": "północy",
        "01": "pierwszej",
        "02": "drugiej", 
        "03": "trzeciej",
        "04": "czwartej",
        "05": "piątej",
        "06": "szóstej",
        "07": "siódmej",
        "08": "ósmej",
        "09": "dziewiątej",
        "10": "dziesiątej",
        "11": "jedenastej",
        "12": "dwunastej",
        "13": "trzynastej",
        "14": "czternastej",
        "15": "piętnastej",
        "16": "szesnastej",
        "17": "siedemnastej",
        "18": "osiemnastej",
        "19": "dziewiętnastej",
        "20": "dwudziestej",
        "21": "dwudziestej pierwszej",
        "22": "dwudziestej drugiej",
        "23": "dwudziestej trzeciej"
    }
    
    # Polish minute names for 1-9
    polish_minutes_1_9 = {
        "01": "zero jeden",
        "02": "zero dwa", 
        "03": "zero trzy",
        "04": "zero cztery",
        "05": "zero pięć",
        "06": "zero sześć",
        "07": "zero siedem",
        "08": "zero osiem",
        "09": "zero dziewięć"
    }
    
    # Polish minute names for 10+
    polish_minutes_10_plus = {
        "10": "dziesięć",
        "11": "jedenaście",
        "12": "dwanaście",
        "13": "trzynaście",
        "14": "czternaście",
        "15": "piętnaście",
        "16": "szesnaście",
        "17": "siedemnaście",
        "18": "osiemnaście",
        "19": "dziewiętnaście",
        "20": "dwadzieścia",
        "21": "dwadzieścia jeden",
        "22": "dwadzieścia dwa",
        "23": "dwadzieścia trzy",
        "24": "dwadzieścia cztery",
        "25": "dwadzieścia pięć",
        "26": "dwadzieścia sześć",
        "27": "dwadzieścia siedem",
        "28": "dwadzieścia osiem",
        "29": "dwadzieścia dziewięć",
        "30": "trzydzieści",
        "31": "trzydzieści jeden",
        "32": "trzydzieści dwa",
        "33": "trzydzieści trzy",
        "34": "trzydzieści cztery",
        "35": "trzydzieści pięć",
        "36": "trzydzieści sześć",
        "37": "trzydzieści siedem",
        "38": "trzydzieści osiem",
        "39": "trzydzieści dziewięć",
        "40": "czterdzieści",
        "41": "czterdzieści jeden",
        "42": "czterdzieści dwa",
        "43": "czterdzieści trzy",
        "44": "czterdzieści cztery",
        "45": "czterdzieści pięć",
        "46": "czterdzieści sześć",
        "47": "czterdzieści siedem",
        "48": "czterdzieści osiem",
        "49": "czterdzieści dziewięć",
        "50": "pięćdziesiąt",
        "51": "pięćdziesiąt jeden",
        "52": "pięćdziesiąt dwa",
        "53": "pięćdziesiąt trzy",
        "54": "pięćdziesiąt cztery",
        "55": "pięćdziesiąt pięć",
        "56": "pięćdziesiąt sześć",
        "57": "pięćdziesiąt siedem",
        "58": "pięćdziesiąt osiem",
        "59": "pięćdziesiąt dziewięć"
    }
    
    # Pattern to match hour formats with any minutes
    # Matches: od godziny XX:XX, od XX:XX, do godziny XX:XX, do XX:XX, o godzinie XX:XX, o XX:XX
    pattern = r'\b(od godziny|od|do godziny|do|o godzinie|o)\s+(\d{1,2}):(\d{2})\b'
    
    def replace_hour(match):
        prefix = match.group(1)
        hour = match.group(2)
        minutes = match.group(3)
        
        # Handle midnight (00:00) specially
        if hour == "00" and minutes == "00":
            if prefix in ["od godziny", "od"]:
                return "od północy"
            elif prefix in ["do godziny", "do"]:
                return "do północy"
            elif prefix in ["o godzinie", "o"]:
                return "o północy"
        
        # Get the Polish hour name
        polish_hour = polish_hours.get(hour, hour)
        
        # Handle minutes
        if minutes == "00":
            # Full hour - just return the hour
            return f"{prefix} {polish_hour}"
        elif minutes in polish_minutes_1_9:
            # Minutes 1-9: "zero trzy"
            polish_minutes = polish_minutes_1_9[minutes]
            return f"{prefix} {polish_hour} {polish_minutes}"
        elif minutes in polish_minutes_10_plus:
            # Minutes 10+: "trzydzieści dziewięć"
            polish_minutes = polish_minutes_10_plus[minutes]
            return f"{prefix} {polish_hour} {polish_minutes}"
        else:
            # Fallback to original if minutes not found
            return match.group(0)
    
    # Apply the replacement
    result = re.sub(pattern, replace_hour, text)
    
    return result