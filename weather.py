# weather.py (Enhanced with multiple free weather APIs)
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def weather():
    # Try OpenWeatherMap first (if API key exists)
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if api_key:
        try:
            # Get location based on IP
            ip_response = requests.get('https://ipapi.co/json/', timeout=5)
            if ip_response.status_code == 200:
                data = ip_response.json()
                city = data.get('city')
                if city:
                    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        weather_data = response.json()
                        temp = weather_data['main']['temp']
                        desc = weather_data['weather'][0]['description']
                        return f"Current weather in {city}: {temp}°C, {desc}"
        except:
            pass
    
    # Fallback 1: wttr.in (Free, no API key needed)
    try:
        response = requests.get('https://wttr.in/?format=%l:+%c+%t', timeout=5)
        if response.status_code == 200:
            return f"Weather: {response.text.strip()}"
    except:
        pass
    
    # Fallback 2: Open-Meteo (Free, no API key needed)
    try:
        # Get location
        ip_response = requests.get('https://ipapi.co/json/', timeout=5)
        if ip_response.status_code == 200:
            data = ip_response.json()
            lat = data.get('latitude')
            lon = data.get('longitude')
            city = data.get('city')
            if lat and lon:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    weather_data = response.json()
                    temp = weather_data['current_weather']['temperature']
                    return f"Current weather in {city}: {temp}°C"
    except:
        pass
    
    return "Weather service temporarily unavailable. Please try again later."