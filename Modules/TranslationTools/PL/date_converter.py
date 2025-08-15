import re

def convert_dates(text: str) -> str:
    """
    Convert date formats in messages from "Piątek 13.04.2025" to "Piątek trzynastego kwietnia".
    
    Converts patterns like:
    - "Piątek 13.04.2025" -> "Piątek trzynastego kwietnia"
    - "Poniedziałek 01.01.2024" -> "Poniedziałek pierwszego stycznia"
    - "Środa 25.12.2024" -> "Środa dwudziestego piątego grudnia"
    
    The year is skipped in the output.
    """
    
    # Polish day names (already in nominative case)
    polish_days = {
        "Poniedziałek": "Poniedziałek",
        "Wtorek": "Wtorek", 
        "Środa": "Środa",
        "Czwartek": "Czwartek",
        "Piątek": "Piątek",
        "Sobota": "Sobota",
        "Niedziela": "Niedziela"
    }
    
    # Polish day numbers in genitive case (dopełniacz)
    polish_day_numbers = {
        "01": "pierwszego",
        "02": "drugiego",
        "03": "trzeciego",
        "04": "czwartego",
        "05": "piątego",
        "06": "szóstego",
        "07": "siódmego",
        "08": "ósmego",
        "09": "dziewiątego",
        "10": "dziesiątego",
        "11": "jedenastego",
        "12": "dwunastego",
        "13": "trzynastego",
        "14": "czternastego",
        "15": "piętnastego",
        "16": "szesnastego",
        "17": "siedemnastego",
        "18": "osiemnastego",
        "19": "dziewiętnastego",
        "20": "dwudziestego",
        "21": "dwudziestego pierwszego",
        "22": "dwudziestego drugiego",
        "23": "dwudziestego trzeciego",
        "24": "dwudziestego czwartego",
        "25": "dwudziestego piątego",
        "26": "dwudziestego szóstego",
        "27": "dwudziestego siódmego",
        "28": "dwudziestego ósmego",
        "29": "dwudziestego dziewiątego",
        "30": "trzydziestego",
        "31": "trzydziestego pierwszego"
    }
    
    # Polish month names in genitive case (dopełniacz)
    polish_months = {
        "01": "stycznia",
        "02": "lutego",
        "03": "marca",
        "04": "kwietnia",
        "05": "maja",
        "06": "czerwca",
        "07": "lipca",
        "08": "sierpnia",
        "09": "września",
        "10": "października",
        "11": "listopada",
        "12": "grudnia"
    }
    
    # Pattern to match: Polish day name + DD.MM.YYYY
    # Matches: Piątek 13.04.2025, Poniedziałek 01.01.2024, etc.
    pattern = r'\b(Poniedziałek|Wtorek|Środa|Czwartek|Piątek|Sobota|Niedziela)\s+(\d{2})\.(\d{2})\.\d{4}\b'
    
    def replace_date(match):
        day_name = match.group(1)
        day_number = match.group(2)
        month_number = match.group(3)
        
        # Get Polish equivalents
        polish_day = polish_days.get(day_name, day_name)
        polish_day_num = polish_day_numbers.get(day_number, day_number)
        polish_month = polish_months.get(month_number, month_number)
        
        # Return in format: "Piątek trzynastego kwietnia"
        return f"{polish_day} {polish_day_num} {polish_month}"
    
    # Apply the replacement
    result = re.sub(pattern, replace_date, text)
    
    return result
