import requests
from bs4 import BeautifulSoup
import re

def weather():
    query = "rishra"  # You can change this to your city
    url = f'https://www.google.com/search?q=weather+{query}'
    
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/137.0.0.0 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find weather data using various selectors
        temp_element = soup.find('span', {'id': 'wob_tm'})
        desc_element = soup.find('span', {'id': 'wob_dc'})
        
        if temp_element and desc_element:
            temp = temp_element.text
            desc = desc_element.text
            
            # Get unit
            unit_element = soup.find('div', {'class': 'vk_bk wob-unit'})
            unit = '°C'
            if unit_element:
                unit_span = unit_element.find('span', {'class': 'wob_t'})
                if unit_span:
                    unit = unit_span.text
            
            return f"The weather in {query} is {temp} {unit} with {desc}"
        else:
            # Alternative method using div
            weather_div = soup.find('div', {'id': 'wob_wc'})
            if weather_div:
                # Try to extract temperature using regex
                temp_match = re.search(r'(\d+)\s*°', str(weather_div))
                if temp_match:
                    temp = temp_match.group(1)
                    desc_match = re.search(r'<span[^>]*id="wob_dc"[^>]*>([^<]+)</span>', str(weather_div))
                    if desc_match:
                        desc = desc_match.group(1)
                        return f"The weather in {query} is {temp}°C with {desc}"
            
            return f"Could not fetch weather for {query}. Please try again."
            
    except requests.exceptions.RequestException as e:
        return f"Sorry, I could not fetch the weather right now."
    except Exception as e:
        return f"Sorry, I could not fetch the weather right now."