# actio.py - Updated with Wikipedia as primary source
import datetime
import json
import os
import urllib.request
import webbrowser
import geocoder
import requests
from geopy.distance import geodesic
import time
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import wikipedia

load_dotenv()

import knowledge
import text_to_speech
import weather
import emergency_guide

# ===== API KEYS =====
HF_API_KEY = os.getenv("HF_API_KEY", "")
HF_MODEL = os.getenv("HF_MODEL", "microsoft/DialoGPT-medium")

# ===== ALERT CONFIGURATION =====
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "")
ALERT_PASSWORD = os.getenv("ALERT_PASSWORD", "")
DISPLAY_ALERTS_ONLY = os.getenv("DISPLAY_ALERTS_ONLY", "false").lower() == "true"

# ===== EMERGENCY FLAGS =====
EMERGENCY_MODE = False
EMERGENCY_ACTIVE = False

# Cache
cache = {
    'location': None,
    'api_response': {},
    'weather': {'data': None, 'timestamp': None},
    'nearby_services': {'data': None, 'timestamp': None}
}
CACHE_DURATION = 300
API_CALL_HISTORY = []

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
    "Your priority is to provide immediate life-saving instructions. "
    "Be extremely clear, calm, and precise. Provide step-by-step first aid instructions. "
    "Ask for location information to dispatch emergency services. "
    "DO NOT waste time with casual conversation. Focus on the emergency at hand."
)

conversation_history = [
    {"role": "user", "parts": [{"text": SYSTEM_PROMPT_REGULAR}]},
    {"role": "model", "parts": [{"text": "Understood. I am MediGuide, your friendly AI assistant. I can help with any topic - from science and history to daily conversations and emergencies. Feel free to ask me anything!"}]},
]

EMERGENCY_KEYWORDS = [
    "heart attack", "chest pain", "difficulty breathing", "choking", "bleeding",
    "burn", "fracture", "broken bone", "seizure", "stroke", "head injury",
    "concussion", "poison", "allergic reaction", "anaphylaxis", "drowning",
    "unconscious", "fainting", "electric shock", "sprain", "eye injury",
    "dental emergency", "nosebleed", "hypothermia", "heat stroke", "bites"
]

# ===== LOCAL RESPONSES =====
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
    "capital of france": "The capital of France is Paris! 🇫🇷",
    "capital of india": "The capital of India is New Delhi! 🇮🇳",
    "capital of usa": "The capital of USA is Washington D.C.! 🇺🇸",
    "capital of uk": "The capital of UK is London! 🇬🇧",
    "capital of japan": "The capital of Japan is Tokyo! 🇯🇵",
    "capital of australia": "The capital of Australia is Canberra! 🇦🇺",
    "largest ocean": "The Pacific Ocean is the largest ocean on Earth.",
    "tallest mountain": "Mount Everest is the tallest mountain at 8,848 meters.",
    "longest river": "The Nile River is the longest river at 6,650 km.",
}

# ===== EMAIL FUNCTIONS =====
def send_email_via_gmail(to_email, subject, body):
    if not ALERT_EMAIL or not ALERT_PASSWORD:
        return False, "Gmail not configured"
    
    try:
        msg = MIMEMultipart()
        msg['From'] = ALERT_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject[:200]
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(ALERT_EMAIL, ALERT_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, "✅ Email sent via Gmail!"
    except Exception as e:
        return False, f"Gmail error: {str(e)}"

def send_emergency_alert(emergency_type, location, user_message, user_name="User"):
    if DISPLAY_ALERTS_ONLY:
        return "📋 Alert displayed in app (Email disabled)"
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    location_info = ""
    if location:
        location_info = f"""
📍 LOCATION:
─────────────────────────────────────────────────────────────
• Address: {location.get('address', 'Unknown')}
• City: {location.get('city', 'Unknown')}
• State: {location.get('state', 'Unknown')}
• Country: {location.get('country', 'Unknown')}
• Coordinates: {location.get('lat', 'Unknown')}, {location.get('lng', 'Unknown')}
"""
    
    alert_body = f"""
╔═══════════════════════════════════════════════════════════╗
║              🚨 EMERGENCY ALERT 🚨                        ║
╚═══════════════════════════════════════════════════════════╝

📋 EMERGENCY DETAILS:
─────────────────────────────────────────────────────────────
• Type: {emergency_type}
• Time: {timestamp}
• User: {user_name}
{location_info}
💬 USER MESSAGE:
─────────────────────────────────────────────────────────────
{user_message}

🔴 ACTION REQUIRED:
─────────────────────────────────────────────────────────────
✅ The user is reporting an emergency situation
✅ Please check on the user immediately
✅ Call emergency services (911) if this is a real emergency

📌 EMERGENCY CONTACTS:
─────────────────────────────────────────────────────────────
• 911 - General Emergency (US/Canada)
• 112 - International Emergency
• 999 - UK Emergency

---
🚑 This is an alert from MediGuide Emergency Assistant
"""
    
    if ALERT_EMAIL and ALERT_PASSWORD:
        success, status = send_email_via_gmail(ALERT_EMAIL, f"🚨 Emergency Alert: {emergency_type}", alert_body)
        if success:
            return status
    
    return "⚠️ No email service configured."

# ===== LOCATION FUNCTIONS =====
def get_cached_location():
    if cache['location'] and cache['location']['timestamp'] and \
       (datetime.datetime.now() - cache['location']['timestamp']).seconds < CACHE_DURATION:
        return cache['location']['data']
    
    try:
        g = geocoder.ip('me')
        if g.latlng:
            location_data = {'lat': g.latlng[0], 'lng': g.latlng[1], 'address': g.address, 'city': g.city, 'state': g.state, 'country': g.country}
            cache['location'] = {'data': location_data, 'timestamp': datetime.datetime.now()}
            return location_data
    except:
        pass
    
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('latitude') and data.get('longitude'):
                location_data = {
                    'lat': data.get('latitude'),
                    'lng': data.get('longitude'),
                    'address': f"{data.get('city')}, {data.get('country_name')}",
                    'city': data.get('city'),
                    'state': data.get('region'),
                    'country': data.get('country_name')
                }
                cache['location'] = {'data': location_data, 'timestamp': datetime.datetime.now()}
                return location_data
    except:
        pass
    
    return None

get_location = get_cached_location

def find_nearby_emergency_services(location, service_type="hospital"):
    if not location:
        return None
    
    lat, lng = location['lat'], location['lng']
    service_tags = {'hospital': 'amenity=hospital', 'police': 'amenity=police', 'ambulance': 'emergency=ambulance_station', 'fire_station': 'amenity=fire_station'}
    tag = service_tags.get(service_type, 'amenity=hospital')
    
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""[out:json];(node["{tag}"](around:5000,{lat},{lng});way["{tag}"](around:5000,{lat},{lng}););out body;"""
    
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
                services.append({'name': name, 'lat': elat, 'lng': elng, 'distance': round(distance, 2), 'type': service_type, 'phone': tags.get('phone', 'Not available'), 'address': tags.get('addr:street', '') + ' ' + tags.get('addr:city', '')})
            return sorted(services, key=lambda x: x['distance'])
    except:
        pass
    return None

def emergency_contact_response(location=None):
    response = "🚨 EMERGENCY ASSISTANCE ACTIVATED 🚨\n\n"
    if location:
        response += f"📍 Location detected: {location.get('address', 'Unknown')}\n📍 Coordinates: {location.get('lat')}, {location.get('lng')}\n\n"
    response += "📞 EMERGENCY CONTACTS (For your reference):\n• 911 - General Emergency (US/Canada)\n• 112 - International Emergency\n• 999 - UK Emergency\n• 102 - Ambulance (India)\n• 100 - Police (India)\n• 101 - Fire (India)\n\n"
    if location:
        response += "🏥 NEARBY EMERGENCY SERVICES (For reference):\n"
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
    strong_emergency = ["emergency", "urgent", "help me", "accident", "injured", "bleeding heavily", "can't breathe", "not breathing", "call ambulance", "need doctor", "heart attack"]
    for phrase in strong_emergency:
        if phrase in text_lower:
            return True
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            return True
    severe_pain_patterns = ["my chest hurts", "my head hurts badly", "severe pain in my", "can't move my", "broken my", "bleeding from my"]
    for pattern in severe_pain_patterns:
        if pattern in text_lower:
            return True
    return False

def _handle_emergency(user_message, location=None):
    global EMERGENCY_MODE, EMERGENCY_ACTIVE
    EMERGENCY_MODE = True
    EMERGENCY_ACTIVE = True
    
    text = user_message.lower()
    response = "🚨 EMERGENCY MODE ACTIVATED 🚨\n\n"
    
    if not location:
        location = get_location()
    
    emergency_type = "Unknown Emergency"
    emergency_map = {
        "heart attack": "Heart Attack", "chest pain": "Heart Attack",
        "choking": "Choking", "can't breathe": "Choking", "not breathing": "Choking",
        "bleeding": "Bleeding", "bleed": "Bleeding",
        "burn": "Burns", "burnt": "Burns",
        "fracture": "Fracture", "broken bone": "Fracture",
        "seizure": "Seizure", "fit": "Seizure",
        "stroke": "Stroke",
        "head injury": "Head Injury", "concussion": "Head Injury",
        "poison": "Poisoning",
        "allergic reaction": "Allergic Reaction", "allergy": "Allergic Reaction",
        "unconscious": "Unconscious", "fainting": "Unconscious",
        "heat stroke": "Heat Stroke",
        "drowning": "Drowning",
        "nosebleed": "Nosebleed",
        "electric shock": "Electric Shock",
        "sprain": "Sprain"
    }
    
    for key, value in emergency_map.items():
        if key in text:
            emergency_type = value
            break
    
    alert_status = send_emergency_alert(emergency_type, location, user_message, "User")
    
    if location:
        response += f"📍 Location: {location.get('address', 'Unknown')}\n"
        if location.get('lat') and location.get('lng'):
            response += f"📍 Coordinates: {location.get('lat')}, {location.get('lng')}\n"
        response += "\n"
    
    response += f"📨 Alert Status: {alert_status}\n\n"
    response += emergency_contact_response(location)
    response += "\n" + "="*50 + "\n\n"
    
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
        response += "Medical emergency detected. Please call emergency services immediately.\nWhile waiting, stay calm and follow these steps:\n1. Call your local emergency number\n2. Don't move the person if they might have a spinal injury\n3. If they're unconscious, check for breathing and start CPR if needed\n4. Keep the person warm and comfortable\n5. Stay with them until help arrives\n"
    
    return _speak_and_return(response)

def get_local_response(user_message):
    user_lower = user_message.lower().strip()
    for key, response in LOCAL_RESPONSES.items():
        if key in user_lower:
            return response
    return None

# ===== WIKIPEDIA - PRIMARY SOURCE (FREE, NO API KEY NEEDED!) =====
def get_answer_from_wikipedia(question):
    """Get answer from Wikipedia - FREE and reliable!"""
    print("\n📚 SEARCHING WIKIPEDIA...")
    print(f"Question: {question}")
    
    try:
        # Extract topic from question
        topic = question
        # Remove common question words
        words_to_remove = ["what is", "who is", "where is", "when is", "why is", "how is", 
                          "what are", "who are", "where are", "when are", "why are", "how are",
                          "tell me about", "define", "explain", "meaning of", "about"]
        
        for word in words_to_remove:
            if question.lower().startswith(word):
                topic = question[len(word):].strip()
                break
        
        # Clean up topic
        topic = topic.strip().strip('?').strip()
        
        if len(topic) < 2:
            print("❌ Topic too short")
            return None
        
        print(f"🔍 Searching for: '{topic}'")
        
        # Search Wikipedia
        search_results = wikipedia.search(topic, results=3)
        print(f"📋 Search results: {search_results}")
        
        if not search_results:
            print("❌ No Wikipedia results found")
            return None
        
        # Get the first result
        page_title = search_results[0]
        print(f"📄 Getting page: {page_title}")
        
        # Get summary
        summary = wikipedia.summary(page_title, sentences=3, auto_suggest=False)
        print(f"✅ Found: {summary[:100]}...")
        
        if summary:
            return f"📚 According to Wikipedia:\n\n{summary}"
        else:
            return None
            
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"⚠️ Ambiguous: {e}")
        # Try the first option
        try:
            summary = wikipedia.summary(e.options[0], sentences=3)
            return f"📚 According to Wikipedia:\n\n{summary}"
        except:
            return None
            
    except wikipedia.exceptions.PageError:
        print("❌ Page not found")
        return None
        
    except wikipedia.exceptions.WikipediaException as e:
        print(f"❌ Wikipedia error: {e}")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

# ===== HUGGING FACE API (FALLBACK ONLY) =====
def chat_with_huggingface(user_message, emergency_mode=False):
    """Use Hugging Face API as fallback"""
    
    print("\n🐍 HUGGING FACE API (FALLBACK)...")
    
    if not HF_API_KEY or HF_API_KEY == "your_huggingface_token_here":
        print("❌ No valid HF_API_KEY")
        return None
    
    if not HF_API_KEY.startswith("hf_"):
        print(f"❌ Invalid API key format")
        return None
    
    # Check internet
    try:
        requests.get('https://api-inference.huggingface.co', timeout=3)
    except:
        print("❌ No internet connection")
        return None
    
    context = f"Question: {user_message}\nAnswer:"
    
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": context,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated = result[0].get('generated_text', '').strip()
                if generated:
                    if "Answer:" in generated:
                        generated = generated.split("Answer:")[-1].strip()
                    if generated and len(generated) > 5:
                        print(f"✅ Hugging Face: {generated[:50]}...")
                        return generated
        else:
            print(f"❌ Hugging Face error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Hugging Face exception: {e}")
        return None
    
    return None

def get_local_fallback(user_message):
    """Final fallback responses"""
    user_lower = user_message.lower()
    
    # Check local knowledge base
    local_response = get_local_response(user_message)
    if local_response:
        return local_response
    
    # Check knowledge module
    knowledge_response = knowledge.get_local_knowledge(user_message)
    if knowledge_response:
        return knowledge_response
    
    # Common questions
    if "weather" in user_lower:
        return weather.weather()
    elif "joke" in user_lower:
        return knowledge.tell_joke()
    elif "fact" in user_lower:
        return knowledge.tell_fact()
    elif "time" in user_lower:
        return f"The time is {datetime.datetime.now().strftime('%I:%M %p')}"
    elif "date" in user_lower:
        return f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}"
    
    return "I couldn't find information on that topic. Try asking about something else, or check your internet connection."

def _chat_with_api(user_message, emergency_mode=False):
    """Main API router - Wikipedia first, then Hugging Face"""
    
    print("\n" + "="*60)
    print(f"🔍 PROCESSING: {user_message}")
    print("="*60)
    
    # 1. Check local responses
    local_response = get_local_response(user_message)
    if local_response:
        print("✅ Using local response")
        return local_response
    
    # 2. Check knowledge module
    knowledge_response = knowledge.get_local_knowledge(user_message)
    if knowledge_response:
        print("✅ Using knowledge module")
        return knowledge_response
    
    # 3. Try Wikipedia (FREE, NO API KEY!)
    wiki_response = get_answer_from_wikipedia(user_message)
    if wiki_response:
        print("✅ Using Wikipedia response")
        return wiki_response
    
    # 4. Try Hugging Face (Fallback)
    hf_response = chat_with_huggingface(user_message, emergency_mode)
    if hf_response:
        print("✅ Using Hugging Face response")
        return hf_response
    
    # 5. Final fallback
    print("❌ All sources failed, using fallback")
    return get_local_fallback(user_message)

# ===== MAIN ACTION FUNCTION =====
def Action(data):
    global EMERGENCY_MODE, EMERGENCY_ACTIVE
    
    if not data:
        return _speak_and_return("I did not catch that. Please say or type it again.")

    user_data = data.strip()
    user_data_lower = user_data.lower()

    if "exit emergency mode" in user_data_lower or "emergency over" in user_data_lower:
        EMERGENCY_MODE = False
        EMERGENCY_ACTIVE = False
        reset_conversation()
        return _speak_and_return("Emergency mode deactivated. I'm back to regular conversation mode.")

    if _is_emergency(user_data_lower):
        location = get_location()
        return _handle_emergency(user_data_lower, location)
    
    if EMERGENCY_MODE:
        return _speak_and_return("🚨 You are in emergency mode. Please describe the emergency or say 'exit emergency mode' to return to regular conversation.")

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

    answer = _chat_with_api(user_data, EMERGENCY_MODE)
    return _speak_and_return(answer)

def reset_conversation():
    global EMERGENCY_MODE, EMERGENCY_ACTIVE
    EMERGENCY_MODE = False
    EMERGENCY_ACTIVE = False
    conversation_history[:] = [
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT_REGULAR}]},
        {"role": "model", "parts": [{"text": "Understood. I am MediGuide, your friendly AI assistant. I can help with any topic - from science and history to daily conversations and emergencies. Feel free to ask me anything!"}]},
    ]