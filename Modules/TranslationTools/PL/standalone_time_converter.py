import re

def convert_standalone_time(text: str) -> str:
    """
    Convert standalone time formats (HH:MM) to Polish text format.
    
    Converts patterns like:
    - "00:00" -> "północ"
    - "00:15" -> "piętnaście po północy"
    - "01:12" -> "pierwsza dwanaście"
    - "23:59" -> "dwudziesta trzecia pięćdziesiąt dziewięć"
    - "16:11" -> "szesnasta jedenaście"
    - "20:05" -> "dwudziesta zero pięć"
    
    Rules:
    - If midnight (00:XX), read as "X po północy"
    - If minutes have leading zero (XX:0Y), read as "zero Y"
    - If minutes are 10+, read normally
    - Hours are in nominative case (pierwsza, druga, etc.)
    """
    
    polish_hours_nominative = {
        "00": "północ",
        "01": "pierwsza",
        "02": "druga", 
        "03": "trzecia",
        "04": "czwarta",
        "05": "piąta",
        "06": "szósta",
        "07": "siódma",
        "08": "ósma",
        "09": "dziewiąta",
        "10": "dziesiąta",
        "11": "jedenasta",
        "12": "dwunasta",
        "13": "trzynasta",
        "14": "czternasta",
        "15": "piętnasta",
        "16": "szesnasta",
        "17": "siedemnasta",
        "18": "osiemnasta",
        "19": "dziewiętnasta",
        "20": "dwudziesta",
        "21": "dwudziesta pierwsza",
        "22": "dwudziesta druga",
        "23": "dwudziesta trzecia"
    }
    
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
    
    pattern = r'\b(\d{1,2}):(\d{2})\b'
    
    def replace_standalone_time(match):
        hour = match.group(1)
        minutes = match.group(2)
        
        if hour == "00":
            if minutes == "00":
                return "północ"
            elif minutes in polish_minutes_1_9:
                polish_minutes = polish_minutes_1_9[minutes]
                return f"{polish_minutes} po północy"
            elif minutes in polish_minutes_10_plus:
                polish_minutes = polish_minutes_10_plus[minutes]
                return f"{polish_minutes} po północy"
            else:
                return match.group(0)
        
        polish_hour = polish_hours_nominative.get(hour, hour)
        
        if minutes == "00":
            return polish_hour
        elif minutes in polish_minutes_1_9:
            polish_minutes = polish_minutes_1_9[minutes]
            return f"{polish_hour} {polish_minutes}"
        elif minutes in polish_minutes_10_plus:
            polish_minutes = polish_minutes_10_plus[minutes]
            return f"{polish_hour} {polish_minutes}"
        else:
            return match.group(0)
    
    result = re.sub(pattern, replace_standalone_time, text)
    
    return result
