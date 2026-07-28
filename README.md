MediGuide - Smart Emergency Assistant 🚑
📋 Overview
MediGuide is an intelligent voice-enabled assistant built in Python that provides emergency medical guidance, general knowledge queries, weather information, and location-based services. It features both text and voice interfaces with automatic emergency detection and email alerting capabilities.

**Key Features**:

 1.   🆘 Emergency Detection & Response - Automatically detects medical emergencies and provides first aid instructions

 2.  📧 Email Alerts - Sends formatted emergency alerts with location details via Gmail

 3.  🎤 Voice Interface - Speech-to-text and text-to-speech capabilities

 4. 📚 Wikipedia Integration - Primary knowledge source (FREE, no API key needed!)

 5.  🏥 Location Services - Finds nearby hospitals, police stations, and fire stations

 6.   🌤️ Weather Updates - Multi-API weather system with fallback support

 7.   💬 Conversational AI - Natural language processing for general queries

**📁 Project Structure**
    MediGuide/
├── actio.py              # Main logic, API routing, emergency handling
├── gui.py                # Tkinter GUI interface
├── knowledge.py          # Local knowledge base and facts
├── speech_to_text.py     # Voice input using speech_recognition
├── text_to_speech.py     # Voice output using pyttsx3
├── weather.py            # Weather data from multiple free APIs
├── emergency_guide.py    # First aid instructions (required)
├── .env                  # Configuration file (create this)
└── requirements.txt      # Python dependencies

**🚀 Quick Start**
Prerequisites
    Python 3.7 or higher

    Microphone (for voice features)

    Internet connection (for Wikipedia, weather, location services)

    Gmail account (for emergency email alerts)

**Installation**
    Clone the repository

    bash
    git clone <repository-url>
    cd MediGuide
    Install dependencies

    bash
    pip install -r requirements.txt
    Create .env file

    bash
    # Create a .env file in the project root with:
    ALERT_EMAIL=your_email@gmail.com
    ALERT_PASSWORD=your_gmail_app_password
    # Optional - Weather API (works without it)
    OPENWEATHER_API_KEY=your_openweather_api_key
    Run the application

    bash
    python gui.py
    🔧 Configuration
    Environment Variables (.env)
    Variable	Required	Description
    ALERT_EMAIL	✅ Yes	Your Gmail address for sending emergency alerts
    ALERT_PASSWORD	✅ Yes	Gmail App Password (NOT your regular password)
    OPENWEATHER_API_KEY	❌ No	Optional - for more accurate weather data
    DISPLAY_ALERTS_ONLY	❌ No	Set to "true" to disable email sending (for testing)
    Setting up Gmail App Password
    Go to your Google Account → Security

    Enable 2-Factor Authentication

    Go to "App Passwords"

    Select "Mail" and "Other (custom name)"

    Enter "MediGuide" and generate

    Copy the 16-character password to .env

🎯 Features Explained
    1. Emergency Detection System
    MediGuide automatically detects medical emergencies by scanning for keywords:

    python
    EMERGENCY_KEYWORDS = [
        "heart attack", "chest pain", "difficulty breathing", 
        "choking", "bleeding", "burn", "fracture", "seizure", 
        "stroke", "head injury", "concussion", "poison", 
        "allergic reaction", "anaphylaxis", "drowning"
    ]

    When an emergency is detected:

🚨 Emergency Mode activates

    📧 Email alert is sent to configured recipient

    📍 Location is automatically detected

    🏥 Nearby hospitals and emergency services are shown

    📋 Step-by-step first aid instructions are provided

Emergency Types Supported:

    Heart Attack

    Choking

    Severe/Minor Bleeding

    Burns

    Fractures

    Seizures

    Stroke

    Head Injury

    Poisoning

    Allergic Reactions

    Unconsciousness

    Heat Stroke

    Electric Shock

    Drowning

    Nosebleed

    Sprains

2. Knowledge Retrieval System (Multi-Tier Fallback)
text

    1. LOCAL RESPONSES     → Fastest, no API calls
    (Greetings, common questions)

    2. KNOWLEDGE MODULE    → Pre-defined facts
    (Capitals, geography, science)

    3. WIKIPEDIA API       → PRIMARY SOURCE (FREE!)
    (General knowledge, unlimited usage)

    4. LOCAL FALLBACK      → Hardcoded responses
    (Weather, jokes, facts, time)
    Note: Hugging Face API is NOT used - Wikipedia serves as the primary knowledge source with no API key required!

3. Email Alert System
    Emergency alerts include:

    📋 Emergency type and timestamp

    📍 User location (address, city, state, coordinates)

    💬 User's message

    📞 Emergency contact numbers

    🚑 Action required steps

4. Location Services
    Automatic detection via IP address (geocoder)

    Fallback via ipapi.co API

    Nearby services via Overpass API:

    Hospitals (within 5km)

    Police stations

    Fire stations

    Ambulance stations

5. Weather System
    Three-tier fallback system:

    OpenWeatherMap (requires API key - optional)

    wttr.in (free, no API key)

    Open-Meteo (free, no API key)

6. Voice Interface
    Speech-to-Text: Google Speech Recognition (free)

    Text-to-Speech: pyttsx3 (offline, no internet required)

📱 GUI Features
Main Interface
text
┌─────────────────────────────────────────────────────────────┐
│  🚑 MediGuide  Your Intelligent Assistant                  │
│  📍 Location     🤖 AI Status  📧 Email Status             │
│  ⚠️ Emergency Warning                                       │
│  [🏥Hospitals] [🚨Emergency] [🌤️Weather] [😂Joke] [📚Fact]│
├─────────────────────────────────────────────────────────────┤
│  Chat Display Area                                          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  🤖 Welcome message                                 │ │
│  │  👤 User input                                      │ │
│  │  🤖 Bot response                                    │ │
│  └───────────────────────────────────────────────────────┘ │
│  [Input Box                    ] [Send] [🎤Speak]          │
│  💡 Type your question and press Enter                      │
├─────────────────────────────────────────────────────────────┤
│  [🗑️ Clear Chat]                         ✅ Ready          │
└─────────────────────────────────────────────────────────────┘
Quick Action Buttons
Find Hospitals - Locates nearest hospitals

Emergency Help - Triggers emergency mode

Weather - Get current weather

Joke - Tells a random joke

Fact - Tells an interesting fact

**🔄 How It Works - Technical Flow**
    Normal Conversation Flow
    text
    User Input → GUI/Text/Voice
        ↓
    Action() function in actio.py
        ↓
    Check emergency keywords → If emergency → Handle emergency
        ↓
    Check local commands (weather, find hospital, etc.)
        ↓
    Knowledge retrieval chain:
        ├── Local responses (dictionary)
        ├── Knowledge module (local facts)
        ├── Wikipedia API (PRIMARY SOURCE)
        └── Local fallback (hardcoded)
        ↓
    Display response + Text-to-speech
    Emergency Flow
    text
    Emergency detected → Emergency Mode activated
        ↓
    Get user location (IP-based)
        ↓
    Determine emergency type
        ↓
    SEND EMAIL ALERT:
        ├── Format email with location
        ├── Connect to Gmail SMTP
        ├── Send via TLS encryption
        └── Confirm delivery
        ↓
    Find nearby emergency services
        ↓
    Display emergency contacts
        ↓
    Provide first aid instructions
        ↓
    Voice output + GUI display

**🛠️ Dependencies**
    Core Dependencies
    txt
    tkinter                 # GUI framework (built-in)
    requests                # HTTP requests for APIs
    geocoder                # IP-based location detection
    geopy                   # Distance calculations for nearby services
    python-dotenv           # Environment variable management
    wikipedia-api           # Wikipedia knowledge access
    pyttsx3                 # Text-to-speech (offline)
    SpeechRecognition       # Voice input
    pyaudio                 # Microphone access (for SpeechRecognition)
    pyjokes                 # Jokes database
    Optional Dependencies
    txt
    python-dotenv           # For .env file support
    openweather-api         # If using OpenWeatherMap

**📝 Example Queries**
    General Knowledge
    text
    "What is the capital of France?"
    "Tell me about black holes"
    "Who was Albert Einstein?"
    "What is photosynthesis?"
    "How to make pasta?"
    Emergencies (Triggers Alert)
    text
    "I'm having chest pain!" → Heart Attack response + Email
    "I'm choking!" → Choking first aid + Email
    "I have a severe burn!" → Burn treatment + Email
    "Help me, I'm bleeding heavily!" → Bleeding response + Email
    Commands
    text
    "weather" or "what's the weather?"
    "tell me a joke"
    "tell me a fact"
    "find hospital" or "nearest hospital"
    "find police" or "nearest police"
    "what time is it?"
    "open YouTube"
    "clear chat"
    "exit emergency mode"
    🔒 Security & Privacy
    Email Security
    Uses Gmail App Password (not your regular password)

    TLS encryption for all email communications

    Passwords stored in .env file (never hardcoded)

    Location Privacy
    Location is only used during emergencies

    IP-based geolocation (approximate location only)

    No location data is stored permanently

    Data Storage
    No user data is stored or logged

    No cloud storage of conversations

    All processing is done locally

**🐛 Troubleshooting**

    Common Issues & Solutions
    Issue	Solution
    Email not sending	Check Gmail App Password is correct; Enable "Less Secure Apps" or use App Password
    Voice not working	Check microphone permissions; Install pyaudio properly
    Wikipedia not working	Check internet connection; Wikipedia API might be down
    Weather not working	System uses fallback APIs; should still work
    Location not detected	Check internet; IP-based geolocation may be blocked
    TTS not working	Check speaker; pyttsx3 might need additional drivers
    Voice Setup (pyaudio issues)
    Windows:

    bash
    pip install pipwin
    pipwin install pyaudio
    Linux:

    bash
    sudo apt-get install python3-pyaudio
    pip install pyaudio
    Mac:

    bash
    brew install portaudio
    pip install pyaudio
    Gmail SMTP Issues
    Enable 2-Factor Authentication

    Generate App Password (16 characters)

    Use App Password in .env (not regular password)

    Check firewall allows port 587

**📊 Performance**
    Feature	Response Time	Dependencies
    Local Responses	< 100ms	None
    Knowledge Module	< 100ms	None
    Wikipedia Query	500ms - 2s	Internet
    Weather Data	500ms - 1.5s	Internet
    Emergency Email	1s - 3s	Internet + Gmail
    Voice Recognition	1s - 2s	Internet (Google API)
    TTS Output	< 500ms	None (offline)

**🚀 Future Improvements**
    □ GPS-based location (instead of IP-based)
    □ SMS alerts for emergency notifications
    □ Integration with emergency services APIs
    □ Offline Wikipedia caching
    □ Multiple language support
    □ Emergency contact list management
    □ Audio recording of emergency calls
    □ Medical history input for better emergency response

**📄 License**
    This project is for educational purposes. Use responsibly - this is NOT a replacement for professional medical advice or emergency services.

**⚠️ Important Disclaimer**
    MediGuide is an informational assistant only.

    ❌ This is NOT a medical device

    ❌ This does NOT replace professional medical advice

    ❌ This does NOT replace emergency services (911/112/999)

    ✅ ALWAYS call emergency services in a life-threatening situation

    ✅ Use this app only as a supplementary information tool

**👨‍💻 Developer Notes**
    Architecture Decision: Why Wikipedia Over Hugging Face
    Factor	Wikipedia	Hugging Face
    API Key	❌ Not needed	✅ Required
    Cost	100% Free	Free tier limited
    Setup Time	Instant	Requires configuration
    Reliability	Very high	Rate limited
    Response Quality	Fact-checked	May hallucinate
    Maintenance	None	Regular updates needed
    Key Design Patterns Used
    Chain of Responsibility - Multi-tier knowledge retrieval

    Fallback Pattern - Multiple data sources with fallbacks

    Observer Pattern - GUI updates on response

    Singleton Pattern - TTS engine initialization

    Strategy Pattern - Multiple weather APIs

**📞 Support**
    For issues or questions:

    Check the Troubleshooting section

    Verify all dependencies are installed

    Check internet connectivity

    Ensure .env file is properly configured

🙏 Acknowledgments
    Wikipedia - Primary knowledge source

    Google Speech API - Voice recognition

    wttr.in & Open-Meteo - Weather data

    Overpass API - Location services

    Stay safe and use responsibly! 🚑

