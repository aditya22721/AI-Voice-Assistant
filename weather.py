# weather.py
import requests
import json
import os

def weather():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Please set OPENWEATHER_API_KEY environment variable for weather updates."
    
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
        
        return "Could not fetch weather. Please check your internet connection."
    except:
        return "Weather service temporarily unavailable."