import datetime
import json
import os
import urllib.error
import urllib.request
import webbrowser
import re

import knowledge
import text_to_speech
import weather
import emergency_guide

API_KEY = os.getenv("GEMINI_API_KEY")
API_BASE = os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

SYSTEM_PROMPT = (
    "You are a friendly AI assistant named 'MediGuide' that specializes in emergency medical guidance and daily conversations. "
    "Your primary role is to help people during medical emergencies by providing clear, step-by-step first aid instructions. "
    "When an emergency is mentioned (like heart attack, choking, bleeding, burn, fracture, etc.), prioritize giving immediate "
    "life-saving instructions. Also handle daily conversations naturally. Be calm, clear, and concise. "
    "IMPORTANT: Always remind users to call emergency services (911 or local emergency number) for serious emergencies. "
    "Keep responses focused and actionable."
)

conversation_history = [
    {
        "role": "user",
        "parts": [{"text": SYSTEM_PROMPT}],
    },
    {
        "role": "model",
        "parts": [{"text": "Understood. I am MediGuide, your emergency medical assistant. I will help with emergencies and daily conversations. Always call emergency services for serious situations."}],
    },
]

# Emergency keywords
EMERGENCY_KEYWORDS = [
    "heart attack", "chest pain", "difficulty breathing", "choking", "bleeding",
    "burn", "fracture", "broken bone", "seizure", "stroke", "head injury",
    "concussion", "poison", "allergic reaction", "anaphylaxis", "drowning",
    "unconscious", "fainting", "electric shock", "sprain", "eye injury",
    "dental emergency", "nosebleed", "hypothermia", "heat stroke", "bites"
]

def _speak_and_return(message):
    text_to_speech.text_to_speech(message)
    return message

def _is_emergency(text):
    """Check if the user message indicates a medical emergency"""
    text_lower = text.lower()
    # Check for explicit emergency phrases
    emergency_phrases = ["emergency", "urgent", "help", "accident", "injured", 
                        "bleeding heavily", "can't breathe", "not breathing"]
    
    for phrase in emergency_phrases:
        if phrase in text_lower:
            return True
    
    # Check for specific emergency types
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_lower:
            return True
            
    # Check for "my [body part] hurts" patterns
    pain_patterns = ["my head hurts", "my chest hurts", "my stomach hurts", 
                    "my arm hurts", "my leg hurts", "pain in my"]
    for pattern in pain_patterns:
        if pattern in text_lower:
            return True
            
    return False

def _handle_emergency(user_message):
    """Handle emergency queries with immediate first aid guidance"""
    text = user_message.lower()
    
    # Check for specific emergency types and provide targeted guidance
    if "heart attack" in text or "chest pain" in text:
        return _speak_and_return(emergency_guide.heart_attack())
    elif "choking" in text or "can't breathe" in text or "not breathing" in text:
        return _speak_and_return(emergency_guide.choking())
    elif "bleeding" in text or "bleed" in text:
        if "heavy" in text or "severe" in text:
            return _speak_and_return(emergency_guide.severe_bleeding())
        else:
            return _speak_and_return(emergency_guide.minor_bleeding())
    elif "burn" in text or "burnt" in text:
        return _speak_and_return(emergency_guide.burns())
    elif "fracture" in text or "broken bone" in text or "broken arm" in text or "broken leg" in text:
        return _speak_and_return(emergency_guide.fracture())
    elif "seizure" in text or "fit" in text:
        return _speak_and_return(emergency_guide.seizure())
    elif "stroke" in text:
        return _speak_and_return(emergency_guide.stroke())
    elif "head injury" in text or "concussion" in text or "hit my head" in text:
        return _speak_and_return(emergency_guide.head_injury())
    elif "poison" in text or "poisoning" in text:
        return _speak_and_return(emergency_guide.poisoning())
    elif "allergic reaction" in text or "allergy" in text:
        return _speak_and_return(emergency_guide.allergic_reaction())
    elif "unconscious" in text or "fainting" in text or "passed out" in text:
        return _speak_and_return(emergency_guide.unconscious())
    elif "heat stroke" in text or "heatstroke" in text:
        return _speak_and_return(emergency_guide.heat_stroke())
    elif "sprain" in text:
        return _speak_and_return(emergency_guide.sprain())
    elif "electric shock" in text:
        return _speak_and_return(emergency_guide.electric_shock())
    elif "drowning" in text:
        return _speak_and_return(emergency_guide.drowning())
    elif "nosebleed" in text:
        return _speak_and_return(emergency_guide.nosebleed())
    else:
        # Generic emergency response
        return _speak_and_return(
            "This sounds like a medical emergency. Please call emergency services immediately. "
            "While waiting for help, stay calm and follow these steps:\n"
            "1. Call your local emergency number\n"
            "2. Don't move the person if they might have a spinal injury\n"
            "3. If they're unconscious, check for breathing and start CPR if needed\n"
            "4. Keep the person warm and comfortable\n"
            "5. Stay with them until help arrives\n\n"
            "Can you tell me more specifically what happened?"
        )

def _chat_with_api(user_message):
    """Send user message to Gemini API and get response"""
    if not API_KEY:
        return (
            "I can chat about anything once you set your GEMINI_API_KEY. "
            "In PowerShell, run: $env:GEMINI_API_KEY='your_api_key_here'"
        )

    conversation_history.append({
        "role": "user",
        "parts": [{"text": user_message}],
    })

    payload = {
        "contents": conversation_history[-16:],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 500,
            "topP": 0.9,
        },
    }

    request = urllib.request.Request(
        f"{API_BASE}/models/{MODEL}:generateContent?key={API_KEY}",
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
                answer = "I got an empty response from Gemini. Please try again."
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="ignore")
        answer = f"API request failed with status {error.code}. {details[:200]}"
    except Exception as error:
        answer = f"I could not reach Gemini right now: {error}"

    conversation_history.append({
        "role": "model",
        "parts": [{"text": answer}],
    })
    return answer

def Action(data):
    """Main action handler - processes user input and returns response"""
    if not data:
        return _speak_and_return("I did not catch that. Please say or type it again.")

    user_data = data.strip()
    user_data_lower = user_data.lower()

    # Emergency detection - PRIORITY
    if _is_emergency(user_data_lower):
        return _handle_emergency(user_data_lower)

    # Quick commands
    if "what is your name" in user_data_lower:
        return _speak_and_return("My name is MediGuide. I'm here to help with emergencies and daily conversations.")
    
    if "what can you do" in user_data_lower or "help" in user_data_lower and not "help me" in user_data_lower:
        return _speak_and_return(
            "I can help with:\n"
            "• Medical emergencies - tell me what happened\n"
            "• General health questions\n"
            "• Weather updates\n"
            "• Telling jokes and facts\n"
            "• Opening websites\n"
            "• And everyday conversations"
        )

    if "hello" in user_data_lower or "hi" in user_data_lower or "hey" in user_data_lower:
        return _speak_and_return("Hello! I'm MediGuide. How can I assist you today? If you have a medical emergency, tell me what happened.")

    if "good morning" in user_data_lower:
        return _speak_and_return("Good morning! I hope you have a safe day. How can I help you?")

    if "good night" in user_data_lower:
        return _speak_and_return("Good night! Take care and stay safe.")

    if "time" in user_data_lower and ("now" in user_data_lower or "current" in user_data_lower):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return _speak_and_return(f"The time is {current_time}.")

    if "shutdown" in user_data_lower or "exit" in user_data_lower or "close app" in user_data_lower:
        return _speak_and_return("Goodbye! Stay safe and take care.")

    if "play music" in user_data_lower:
        webbrowser.open("https://gaana.com/")
        return _speak_and_return("Opening Gaana for you.")

    if "open youtube" in user_data_lower:
        webbrowser.open("https://youtube.com/")
        return _speak_and_return("Opening YouTube.")

    if "open google" in user_data_lower:
        webbrowser.open("https://google.com/")
        return _speak_and_return("Opening Google.")

    if "weather" in user_data_lower:
        answer = weather.weather()
        return _speak_and_return(answer)

    if "tell me a joke" in user_data_lower:
        return _speak_and_return(knowledge.tell_joke())

    if "tell me a fact" in user_data_lower:
        return _speak_and_return(knowledge.tell_fact())

    if user_data_lower in {"clear chat", "reset chat", "new chat"}:
        reset_conversation()
        return _speak_and_return("Chat reset. I'm ready to help with your health and safety needs.")

    # If no specific commands, use Gemini for general conversation
    answer = _chat_with_api(user_data)
    return _speak_and_return(answer)

def reset_conversation():
    conversation_history[:] = [
        {
            "role": "user",
            "parts": [{"text": SYSTEM_PROMPT}],
        },
        {
            "role": "model",
            "parts": [{"text": "Understood. I am MediGuide, your emergency medical assistant. I will help with emergencies and daily conversations. Always call emergency services for serious situations."}],
        },
    ]