# actio.py (Complete - Using Free Hugging Face API)
import datetime
import json
import os
import urllib.error
import urllib.request
import webbrowser
import re
import geocoder
import requests
from geopy.distance import geodesic
import random
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import knowledge
import text_to_speech
import weather
import emergency_guide

# ===== FREE API CONFIGURATION =====
# Option 1: Hugging Face (100% FREE, no credit card required)
# Get your free token at: https://huggingface.co/settings/tokens
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "microsoft/DialoGPT-medium")
# Alternative models: "google/flan-t5-base", "google/flan-t5-large", "microsoft/DialoGPT-large"

# Option 2: Gemini Free Tier (60 requests/min free)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
API_BASE = os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Choose which API to use (set to 'huggingface' or 'gemini')
USE_API = os.getenv("USE_API", "huggingface")

EMERGENCY_MODE = False

# Cache for API responses
cache = {
    'location': None,
    'api_response': {},
    'weather': {'data': None, 'timestamp': None},
    'nearby_services': {'data': None, 'timestamp': None}
}
CACHE_DURATION = 300  # 5 minutes
API_CALL_HISTORY = []  # For rate limiting

SYSTEM_PROMPT_REGULAR = (
    "You are a friendly AI assistant named 'MediGuide' that can help with ANY topic. "
    "You have access to general knowledge and can answer questions about anything - "
    "science, history, technology, health, relationships, entertainment, etc. "
    "You are also trained in emergency medical guidance. When someone mentions a medical emergency, "
    "you should provide clear, step-by-step first aid instructions. "
    "Be conversational, helpful, and engaging. You can also check weather, tell jokes, and provide facts. "
    "Keep responses friendly and natural. Important: For serious emergencies, always remind users to call emergency services."
)

SYSTEM_PROMPT_EMERGENCY = (
    "You are an emergency response AI assistant. You are currently in EMERGENCY MODE. "
    "Your priority is to provide immediate life-saving instructions and coordinate emergency services. "
    "Be extremely clear, calm, and precise. Provide step-by-step first aid instructions. "
    "Ask for location information to dispatch emergency services. "
    "DO NOT waste time with casual conversation. Focus on the emergency at hand."
)

conversation_history = [
    {
        "role": "user",
        "parts": [{"text": SYSTEM_PROMPT_REGULAR}],
    },
    {
        "role": "model",
        "parts": [{"text": "Understood. I am MediGuide, your friendly AI assistant. I can help with any topic - from science and history to daily conversations and emergencies. Feel free to ask me anything!"}],
    },
]

EMERGENCY_KEYWORDS = [
    "heart attack", "chest pain", "difficulty breathing", "choking", "bleeding",
    "burn", "fracture", "broken bone", "seizure", "stroke", "head injury",
    "concussion", "poison", "allergic reaction", "anaphylaxis", "drowning",
    "unconscious", "fainting", "electric shock", "sprain", "eye injury",
    "dental emergency", "nosebleed", "hypothermia", "heat stroke", "bites"
]

# ===== COMMON RESPONSES (No API needed) =====
LOCAL_RESPONSES = {
    "what is your name": "I'm MediGuide, your intelligent assistant!",
    "who created you": "I was created to help people with their questions and emergencies.",
    "what can you do": "I can help with emergencies, answer questions, tell jokes, check weather, find hospitals, and more!",
    "how are you": "I'm functioning perfectly and ready to help you!",
    "hi": "Hello! How can I help you today?",
    "hello": "Hi there! What can I assist you with?",
    "hey": "Hey! How can I help you?",
    "good morning": "Good morning! How can I assist you today?",
    "good evening": "Good evening! What can I help you with?",
    "thank you": "You're welcome! Is there anything else I can help with?",
    "thanks": "You're welcome! Let me know if you need anything else.",
}

# ===== FREE HUGGING FACE API =====
def chat_with_huggingface(user_message, emergency_mode=False):
    """Use Hugging Face's free inference API"""
    if not HF_API_KEY:
        return "Please set HF_API_KEY in your .env file. Get your free token at: https://huggingface.co/settings/tokens"
    
    # Rate limiting: 30 calls per minute for free tier
    if not can_make_api_call(limit_per_minute=30):
        return "I'm currently handling too many requests. Please wait a moment and try again."
    
    # Format conversation context
    context = f"You are MediGuide, a helpful assistant. Answer: {user_message}"
    
    if emergency_mode:
        context = f"You are an emergency assistant. Provide clear, calm instructions for: {user_message}"
    
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": context,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.8,
            "top_p": 0.9,
            "do_sample": True,
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '').strip()
            elif isinstance(result, dict):
                return result.get('generated_text', '').strip()
            else:
                return str(result)
        elif response.status_code == 503:
            return "The AI model is loading. Please wait 10 seconds and try again."
        else:
            return f"API error: {response.status_code} - {response.text[:200]}"
    except requests.exceptions.Timeout:
        return "The request timed out. Please try again."
    except Exception as e:
        return f"Error with Hugging Face API: {str(e)}"

# ===== FREE GEMINI API (Alternative) =====
def chat_with_gemini(user_message, emergency_mode=False):
    """Use Gemini's free tier (60 requests/min)"""
    if not GEMINI_API_KEY:
        return "Please set GEMINI_API_KEY in your .env file."
    
    if emergency_mode:
        system_prompt = SYSTEM_PROMPT_EMERGENCY
    else:
        system_prompt = SYSTEM_PROMPT_REGULAR
    
    if conversation_history and conversation_history[0]["role"] == "user":
        conversation_history[0]["parts"][0]["text"] = system_prompt

    conversation_history.append({
        "role": "user",
        "parts": [{"text": user_message}],
    })

    payload = {
        "contents": conversation_history[-10:],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 300,
            "topP": 0.9,
        },
    }

    request = urllib.request.Request(
        f"{API_BASE}/models/{MODEL}:generateContent?key={GEMINI_API_KEY}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            parts = data["candidates"][0]["content"]["parts"]
            answer = "".join(part.get("text", "") for part in parts).strip()
            if not answer:
                answer = "I got an empty response. Please try again."
            
            conversation_history.append({
                "role": "model",
                "parts": [{"text": answer}],
            })
            return answer
    except Exception as error:
        return f"Gemini API error: {str(error)}"

# ===== RATE LIMITING =====
def can_make_api_call(limit_per_minute=30):
    """Check rate limit for free APIs"""
    current_time = time.time()
    # Remove calls older than 60 seconds
    API_CALL_HISTORY[:] = [t for t in API_CALL_HISTORY if current_time - t < 60]
    
    if len(API_CALL_HISTORY) < limit_per_minute:
        API_CALL_HISTORY.append(current_time)
        return True
    return False

# ===== LOCATION FUNCTIONS =====
def get_cached_location():
    """Get location with caching"""
    if cache['location'] and cache['location']['timestamp'] and \
       (datetime.datetime.now() - cache['location']['timestamp']).seconds < CACHE_DURATION:
        return cache['location']['data']
    
    try:
        g = geocoder.ip('me')
        if g.latlng:
            location_data = {
                'lat': g.latlng[0],
                'lng': g.latlng[1],
                'address': g.address,
                'city': g.city,
                'state': g.state,
                'country': g.country
            }
            cache['location'] = {
                'data': location_data,
                'timestamp': datetime.datetime.now()
            }
            return location_data
    except:
        pass
    return None

get_location = get_cached_location

def find_nearby_emergency_services(location, service_type="hospital", force_refresh=False):
    """Find nearby services with caching"""
    cache_key = f"{service_type}_{location.get('lat')}_{location.get('lng')}"
    
    if not force_refresh and cache['nearby_services']['data'] and cache['nearby_services']['timestamp']:
        if (datetime.datetime.now() - cache['nearby_services']['timestamp']).seconds < CACHE_DURATION:
            return cache['nearby_services']['data'].get(service_type)
    
    if not location:
        return None
    
    lat, lng = location['lat'], location['lng']
    
    service_tags = {
        'hospital': 'amenity=hospital',
        'police': 'amenity=police',
        'ambulance': 'emergency=ambulance_station',
        'fire_station': 'amenity=fire_station'
    }
    
    tag = service_tags.get(service_type, 'amenity=hospital')
    
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["{tag}"](around:5000,{lat},{lng});
      way["{tag}"](around:5000,{lat},{lng});
    );
    out body;
    """
    
    try:
        response = requests.post(overpass_url, data=query, timeout=10)
        if response.status_code == 200:
            data = response.json()
            elements = data.get('elements', [])
            
            services = []
            for element in elements[:5]:
                tags = element.get('tags', {})
                name = tags.get('name', 'Unknown')
                
                if 'lat' in element:
                    elat, elng = element['lat'], element['lon']
                else:
                    if 'center' in element:
                        elat, elng = element['center']['lat'], element['center']['lon']
                    else:
                        continue
                
                distance = geodesic((lat, lng), (elat, elng)).km
                
                services.append({
                    'name': name,
                    'lat': elat,
                    'lng': elng,
                    'distance': round(distance, 2),
                    'type': service_type,
                    'phone': tags.get('phone', 'Not available'),
                    'address': tags.get('addr:street', '') + ' ' + tags.get('addr:city', '')
                })
            
            sorted_services = sorted(services, key=lambda x: x['distance'])
            
            if not cache['nearby_services']['data']:
                cache['nearby_services']['data'] = {}
            cache['nearby_services']['data'][service_type] = sorted_services
            cache['nearby_services']['timestamp'] = datetime.datetime.now()
            
            return sorted_services
    except Exception as e:
        print(f"Error finding services: {e}")
    
    return None

def emergency_contact_response(location=None):
    response = "🚨 EMERGENCY ASSISTANCE ACTIVATED 🚨\n\n"
    
    if location:
        response += f"📍 Location detected: {location.get('address', 'Unknown')}\n\n"
    
    response += "📞 EMERGENCY CONTACTS:\n"
    response += "• 911 - General Emergency (US/Canada)\n"
    response += "• 112 - International Emergency\n"
    response += "• 999 - UK Emergency\n"
    response += "• 102 - Ambulance (India)\n"
    response += "• 100 - Police (India)\n"
    response += "• 101 - Fire (India)\n\n"
    
    if location:
        response += "🏥 NEARBY EMERGENCY SERVICES:\n"
        
        hospitals = find_nearby_emergency_services(location, 'hospital')
        if hospitals:
            response += "\nHOSPITALS:\n"
            for h in hospitals[:3]:
                response += f"  • {h['name']} - {h['distance']}km away\n"
                if h['phone'] != 'Not available':
                    response += f"    Phone: {h['phone']}\n"
        
        police = find_nearby_emergency_services(location, 'police')
        if police:
            response += "\nPOLICE STATIONS:\n"
            for p in police[:3]:
                response += f"  • {p['name']} - {p['distance']}km away\n"
        
        fire = find_nearby_emergency_services(location, 'fire_station')
        if fire:
            response += "\nFIRE STATIONS:\n"
            for f in fire[:3]:
                response += f"  • {f['name']} - {f['distance']}km away\n"
    
    return response

def _speak_and_return(message):
    text_to_speech.text_to_speech(message)
    return message

def _is_emergency(text):
    text_lower = text.lower()
    
    strong_emergency = ["emergency", "urgent", "help me", "accident", "injured", 
                        "bleeding heavily", "can't breathe", "not breathing", 
                        "call ambulance", "need doctor", "heart attack"]
    
    for phrase in strong_emergency:
        if phrase in text_lower:
            return True
    
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            return True
            
    severe_pain_patterns = ["my chest hurts", "my head hurts badly", "severe pain in my", 
                           "can't move my", "broken my", "bleeding from my"]
    for pattern in severe_pain_patterns:
        if pattern in text_lower:
            return True
            
    return False

def _handle_emergency(user_message, location=None):
    global EMERGENCY_MODE
    EMERGENCY_MODE = True
    
    text = user_message.lower()
    response = "🚨 EMERGENCY MODE ACTIVATED 🚨\n\n"
    
    if not location:
        location = get_location()
    
    if location:
        response += f"📍 Your location: {location.get('address', 'Unknown')}\n"
        response += f"📍 Coordinates: {location.get('lat')}, {location.get('lng')}\n\n"
    
    response += emergency_contact_response(location)
    response += "\n" + "="*50 + "\n\n"
    
    # Emergency guide responses (no API calls needed)
    if "heart attack" in text or "chest pain" in text:
        response += emergency_guide.heart_attack()
    elif "choking" in text or "can't breathe" in text or "not breathing" in text:
        response += emergency_guide.choking()
    elif "bleeding" in text or "bleed" in text:
        if "heavy" in text or "severe" in text:
            response += emergency_guide.severe_bleeding()
        else:
            response += emergency_guide.minor_bleeding()
    elif "burn" in text or "burnt" in text:
        response += emergency_guide.burns()
    elif "fracture" in text or "broken bone" in text:
        response += emergency_guide.fracture()
    elif "seizure" in text or "fit" in text:
        response += emergency_guide.seizure()
    elif "stroke" in text:
        response += emergency_guide.stroke()
    elif "head injury" in text or "concussion" in text:
        response += emergency_guide.head_injury()
    elif "poison" in text or "poisoning" in text:
        response += emergency_guide.poisoning()
    elif "allergic reaction" in text or "allergy" in text:
        response += emergency_guide.allergic_reaction()
    elif "unconscious" in text or "fainting" in text:
        response += emergency_guide.unconscious()
    elif "heat stroke" in text or "heatstroke" in text:
        response += emergency_guide.heat_stroke()
    elif "sprain" in text:
        response += emergency_guide.sprain()
    elif "electric shock" in text:
        response += emergency_guide.electric_shock()
    elif "drowning" in text:
        response += emergency_guide.drowning()
    elif "nosebleed" in text:
        response += emergency_guide.nosebleed()
    else:
        response += "This sounds like a medical emergency. Please call emergency services immediately.\n"
        response += "While waiting for help, stay calm and follow these steps:\n"
        response += "1. Call your local emergency number\n"
        response += "2. Don't move the person if they might have a spinal injury\n"
        response += "3. If they're unconscious, check for breathing and start CPR if needed\n"
        response += "4. Keep the person warm and comfortable\n"
        response += "5. Stay with them until help arrives\n"
    
    return _speak_and_return(response)

def get_local_response(user_message):
    """Check for local responses first"""
    user_lower = user_message.lower().strip()
    for key, response in LOCAL_RESPONSES.items():
        if key in user_lower or user_lower == key:
            return response
    return None

def _chat_with_api(user_message, emergency_mode=False):
    """Main API router - uses free API"""
    global EMERGENCY_MODE
    
    # First check if we have a local response
    local_response = get_local_response(user_message)
    if local_response:
        return local_response
    
    # Route to the selected API
    if USE_API.lower() == "gemini":
        return chat_with_gemini(user_message, emergency_mode)
    else:
        return chat_with_huggingface(user_message, emergency_mode)

def Action(data):
    global EMERGENCY_MODE
    
    if not data:
        return _speak_and_return("I did not catch that. Please say or type it again.")

    user_data = data.strip()
    user_data_lower = user_data.lower()

    if "exit emergency mode" in user_data_lower or "emergency over" in user_data_lower:
        EMERGENCY_MODE = False
        reset_conversation()
        return _speak_and_return("Emergency mode deactivated. I'm back to regular conversation mode.")

    if _is_emergency(user_data_lower):
        location = get_location()
        return _handle_emergency(user_data_lower, location)
    
    if EMERGENCY_MODE:
        return _speak_and_return("🚨 You are in emergency mode. Please describe the emergency or say 'exit emergency mode' to return to regular conversation.")

    # Action commands - These don't use API
    if "open youtube" in user_data_lower:
        webbrowser.open("https://youtube.com/")
        return _speak_and_return("Opening YouTube.")

    if "open google" in user_data_lower:
        webbrowser.open("https://google.com/")
        return _speak_and_return("Opening Google.")
    
    if "play music" in user_data_lower:
        webbrowser.open("https://gaana.com/")
        return _speak_and_return("Opening Gaana for you.")

    if "find hospital" in user_data_lower or "nearest hospital" in user_data_lower:
        location = get_location()
        if location:
            hospitals = find_nearby_emergency_services(location, 'hospital')
            if hospitals:
                response = "🏥 NEARBY HOSPITALS:\n"
                for i, h in enumerate(hospitals[:5], 1):
                    response += f"{i}. {h['name']} - {h['distance']}km away\n"
                    if h['phone'] != 'Not available':
                        response += f"   Phone: {h['phone']}\n"
                return _speak_and_return(response)
            else:
                return _speak_and_return("Sorry, I couldn't find any hospitals nearby. Please call emergency services.")
        else:
            return _speak_and_return("I couldn't determine your location. Please call emergency services directly.")

    if "find police" in user_data_lower or "nearest police" in user_data_lower:
        location = get_location()
        if location:
            police = find_nearby_emergency_services(location, 'police')
            if police:
                response = "👮 NEARBY POLICE STATIONS:\n"
                for i, p in enumerate(police[:5], 1):
                    response += f"{i}. {p['name']} - {p['distance']}km away\n"
                return _speak_and_return(response)
            else:
                return _speak_and_return("Sorry, I couldn't find any police stations nearby.")
        else:
            return _speak_and_return("I couldn't determine your location. Please call emergency services directly.")

    if "weather" in user_data_lower:
        answer = weather.weather()
        return _speak_and_return(answer)

    if "time" in user_data_lower and ("now" in user_data_lower or "current" in user_data_lower):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return _speak_and_return(f"The time is {current_time}.")

    if "tell me a joke" in user_data_lower:
        return _speak_and_return(knowledge.tell_joke())

    if "tell me a fact" in user_data_lower:
        return _speak_and_return(knowledge.tell_fact())

    if "shutdown" in user_data_lower or "exit" in user_data_lower or "close app" in user_data_lower:
        return _speak_and_return("Goodbye! Stay safe and take care.")

    if user_data_lower in {"clear chat", "reset chat", "new chat"}:
        reset_conversation()
        return _speak_and_return("Chat reset. I'm ready to help with your health and safety needs.")

    # Everything else goes to AI API
    answer = _chat_with_api(user_data, EMERGENCY_MODE)
    return _speak_and_return(answer)

def reset_conversation():
    global EMERGENCY_MODE
    EMERGENCY_MODE = False
    conversation_history[:] = [
        {
            "role": "user",
            "parts": [{"text": SYSTEM_PROMPT_REGULAR}],
        },
        {
            "role": "model",
            "parts": [{"text": "Understood. I am MediGuide, your friendly AI assistant. I can help with any topic - from science and history to daily conversations and emergencies. Feel free to ask me anything!"}],
        },
    ]