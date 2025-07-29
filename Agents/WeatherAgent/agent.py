from typing import Dict, Any
from datetime import datetime
import pytz
import requests
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.schema import HumanMessage, SystemMessage
from Agents.agent_base import AgentBase
from Agents.WeatherAgent.tools import get_weather
from Agents.WeatherAgent.constants import day_names, month_names
from config import Config
from suntime import Sun

def convert_numbers_to_polish_words(text: str, llm: ChatOpenAI) -> str:
    prompt = """Zamień wszystkie liczby, daty i godziny w tekście na ich słowną wersję w języku polskim.

Przykłady konwersji:
- "od 23 do 3" → "od dwudziestej trzeciej do trzeciej"
- "o 15" → "o piętnastej"
- "od 5:04" → "od piątej zero cztery"
- "29 lipca" → "dwudziestego dziewiątego lipca"
- "23 lipca" → "dwudziestego trzeciego lipca"
- "1 stycznia" → "pierwszego stycznia"
- "o 12:30" → "o dwunastej trzydzieści"
- "od 19:00 do 23:00" → "od dziewiętnastej do dwudziestej trzeciej"
- "od 14 do 23 stopni Celsjusza" → "od czternastu do dwudziestu trzech stopni Celsjusza"
- "temperatura od 5 do 15 stopni" → "temperatura od pięciu do piętnastu stopni"
- "od 00:00 do 4:00" → "od północy do czwartej rano"
- "o 6:30" → "o szóstej trzydzieści rano"
- "od 1:00 do 9:00" → "od pierwszej do dziewiątej rano"

Zasady:
1. Godziny zamieniaj na liczebniki porządkowe (pierwsza, druga, trzecia, czwarta, piąta, szósta, siódma, ósma, dziewiąta, dziesiąta, jedenasta, dwunasta, trzynasta, czternasta, piętnasta, szesnasta, siedemnasta, osiemnasta, dziewiętnasta, dwudziesta, dwudziesta pierwsza, dwudziesta druga, dwudziesta trzecia)
2. Daty zamieniaj na liczebniki porządkowe w dopełniaczu (pierwszego, drugiego, trzeciego, czwartego, piątego, szóstego, siódmego, ósmego, dziewiątego, dziesiątego, jedenastego, dwunastego, trzynastego, czternastego, piętnastego, szesnastego, siedemnastego, osiemnastego, dziewiętnastego, dwudziestego, dwudziestego pierwszego, dwudziestego drugiego, dwudziestego trzeciego, dwudziestego czwartego, dwudziestego piątego, dwudziestego szóstego, dwudziestego siódmego, dwudziestego ósmego, dwudziestego dziewiątego, trzydziestego, trzydziestego pierwszego)
3. Temperatury zamieniaj na liczebniki kardynalne w dopełniaczu (od pięciu, od sześciu, od siedmiu, od ośmiu, od dziewięciu, od dziesięciu, od jedenastu, od dwunastu, od trzynastu, od czternastu, od piętnastu, od szesnastu, od siedemnastu, od osiemnastu, od dziewiętnastu, od dwudziestu, od dwudziestu jeden, od dwudziestu dwóch, od dwudziestu trzech, do pięciu, do sześciu, do siedmiu, do ośmiu, do dziewięciu, do dziesięciu, do jedenastu, do dwunastu, do trzynastu, do czternastu, do piętnastu, do szesnastu, do siedemnastu, do osiemnastu, do dziewiętnastu, do dwudziestu, do dwudziestu jeden, do dwudziestu dwóch, do dwudziestu trzech)
4. Godzina 00:00 to "północ" np. od 00:00 do 4:00 to "od północy do czwartej rano"
5. Godziny od 1:00 do 9:00 dodaj "rano" (np. "pierwszej rano", "szóstej rano", "dziewiątej rano")
6. Minuty czytaj jako osobne liczby (np. "zero cztery" dla 04, "trzydzieści" dla 30)
7. Zachowaj wszystkie inne elementy tekstu bez zmian

Tekst do konwersji:
{text}

Odpowiedz tylko przekonwertowanym tekstem, bez dodatkowych komentarzy."""
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=text)
    ]
    
    response = llm.invoke(messages)
    return response.content.strip()

class WeatherAgent(AgentBase):
    
    def __init__(self, user_id: str, configuration: dict, questionnaire_answers: dict = None):
        super().__init__(user_id, configuration, questionnaire_answers)
        self.config = Config.from_env()
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.gpt_model,
            temperature=self.configuration.get('temperature', 0)
        )
    
    def _get_user_city_info(self) -> tuple[str, float, float]:
        city_name = self.questionnaire_answers.get('city_name')
        city_lat = self.questionnaire_answers.get('city_lat')
        city_lon = self.questionnaire_answers.get('city_lon')
        
        if city_name and city_lat and city_lon:
            return city_name, city_lat, city_lon
        return None, None, None
    
    def _extract_city_name(self, message: str) -> str:
        system_prompt = """Wyciągnij nazwę miasta z wiadomości użytkownika i przekonwertuj ją do formy podstawowej (mianownik).
        Przykłady:
        - "w paryżu" -> "Paryż"
        - "w Katowicach" -> "Katowice"
        - "w Warszawie" -> "Warszawa"
        - "w Krakowie" -> "Kraków"
        - "w Gdańsku" -> "Gdańsk"
        - "w Wrocławiu" -> "Wrocław"
        - "w Poznaniu" -> "Poznań"
        - "w Łodzi" -> "Łódź"
        - "w Szczecinie" -> "Szczecin"
        - "w Bydgoszczy" -> "Bydgoszcz"
        
        Jeśli nie ma wzmianki o mieście, zwróć 'NO_CITY_FOUND'.
        Zwróć tylko nazwę miasta w formie podstawowej, nic więcej."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=message)
        ]
        
        response = self.llm.invoke(messages)
        city = response.content.strip()
        
        if city == "NO_CITY_FOUND" or not city:
            return None
        return city
    
    def _get_coordinates(self, city_name: str) -> tuple[float, float]:
        geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": city_name,
            "limit": 1,
            "appid": self.config.open_weather_map_api_key
        }
        
        try:
            response = requests.get(geocoding_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return data[0]["lat"], data[0]["lon"]
            else:
                return None, None
        except Exception:
            return None, None
    
    def _format_weather_response(self, weather_data: Dict[str, Any], lat: float, lon: float, city_name: str) -> str:
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
            rain_times = self._format_hour_ranges(rain_hours)
            response += f"Opady deszczu przewidywane są {rain_times}. "
        
        if snow_hours:
            snow_times = self._format_hour_ranges(snow_hours)
            response += f"Śnieg może padać {snow_times}. "
        
        if fog_hours:
            fog_times = self._format_hour_ranges(fog_hours)
            response += f"Mgła może wystąpić {fog_times}. "
        
        if strong_wind_hours:
            wind_times = self._format_hour_ranges(strong_wind_hours)
            response += f"Silny wiatr przewidywany jest {wind_times}. "
        
        if cloudy_hours:
            cloudy_times = self._format_hour_ranges(cloudy_hours)
            response += f"Zachmurzenie duże {cloudy_times}. "
        
        if clear_hours:
            clear_times = self._format_hour_ranges(clear_hours)
            response += f"Bezchmurne niebo {clear_times}. "
        
        if not any([rain_hours, snow_hours]):
            response += "Nie przewiduje się opadów. "
        

        try:
            sun = Sun(lat, lon)
            today = datetime.now()
            
            sunrise = sun.get_sunrise_time(today)
            sunset = sun.get_sunset_time(today)
            
            if sunrise and sunset:
                poland_tz = pytz.timezone('Europe/Warsaw')
                sunrise_poland = sunrise.astimezone(poland_tz)
                sunset_poland = sunset.astimezone(poland_tz)
                
                sunrise_str = sunrise_poland.strftime("%H:%M")
                sunset_str = sunset_poland.strftime("%H:%M")
                response += f"Wschód słońca będzie o {sunrise_str}, a zachód o {sunset_str}."
            else:
                response += "."
        except Exception as e:
            print(f"Error calculating sunrise/sunset: {e}")
            response += "."
        
        return response
    
    def _format_hour_ranges(self, hours: list) -> str:
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
    
    def ask(self, message: str) -> str:
        user_city_name, user_city_lat, user_city_lon = self._get_user_city_info()
        
        city_name = self._extract_city_name(message)
        
        if not city_name:
            if user_city_name:
                city_name = user_city_name
                lat, lon = user_city_lat, user_city_lon
            else:
                return "Nie mogę podać prognozy pogody bez znajomości nazwy miasta. Proszę podać nazwę miasta lub skonfiguruj domyślne miasto w ustawieniach."
        else:
            if user_city_name and city_name.lower() == user_city_name.lower():
                lat, lon = user_city_lat, user_city_lon
            else:
                lat, lon = self._get_coordinates(city_name)
        
        if lat is None or lon is None:
            return f"Przepraszam, nie udało się znaleźć współrzędnych dla '{city_name}'. Sprawdź nazwę miasta i spróbuj ponownie."
        
        weather_data = get_weather(lat, lon)
        response = self._format_weather_response(weather_data, lat, lon, city_name)
        return convert_numbers_to_polish_words(response, self.llm)
    
    @property
    def name(self) -> str:
        return "weather" 