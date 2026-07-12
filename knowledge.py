# knowledge.py (Enhanced with local knowledge)
import random
import wikipedia
import pyjokes

# Local knowledge base (no API needed)
LOCAL_KNOWLEDGE = {
    "capital of france": "Paris is the capital of France.",
    "capital of india": "New Delhi is the capital of India.",
    "capital of usa": "Washington D.C. is the capital of the USA.",
    "capital of uk": "London is the capital of the United Kingdom.",
    "capital of japan": "Tokyo is the capital of Japan.",
    "capital of australia": "Canberra is the capital of Australia.",
    "largest ocean": "The Pacific Ocean is the largest ocean on Earth.",
    "largest continent": "Asia is the largest continent.",
    "tallest mountain": "Mount Everest is the tallest mountain at 8,848 meters.",
    "longest river": "The Nile River is the longest river at 6,650 km.",
    "human body": "The human body has about 206 bones and 600 muscles.",
    "earth population": "Earth's population is approximately 8 billion people.",
    "speed of light": "The speed of light is approximately 299,792,458 meters per second.",
    "water formula": "Water is H2O - two hydrogen atoms and one oxygen atom.",
    "gravity": "Gravity is the force that attracts objects with mass toward each other.",
}

def get_local_knowledge(question):
    """Check local knowledge base first"""
    question_lower = question.lower().strip()
    for key, answer in LOCAL_KNOWLEDGE.items():
        if key in question_lower:
            return answer
    return None

def tell_joke():
    try:
        return pyjokes.get_joke(language='en', category='neutral')
    except:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a fake noodle? An impasta!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "What's orange and sounds like a parrot? A carrot!",
            "Why don't eggs tell jokes? They'd crack each other up!",
        ]
        return random.choice(jokes)

def tell_fact():
    facts = [
        "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old!",
        "Octopuses have three hearts and blue blood.",
        "Bananas are berries, but strawberries are not.",
        "Sharks existed before trees did—over 400 million years ago!",
        "The Eiffel Tower can be 15 cm taller during the summer due to heat expansion.",
        "A day on Venus is longer than a year on Venus.",
        "The human nose can remember 50,000 different scents.",
        "A group of flamingos is called a 'flamboyance'.",
        "The shortest war in history lasted only 38 minutes between Britain and Zanzibar.",
        "A single cloud can weigh more than 1 million pounds.",
    ]
    return random.choice(facts)

def get_knowledge(topic):
    # First check local knowledge
    local_answer = get_local_knowledge(topic)
    if local_answer:
        return local_answer
    
    # Then try Wikipedia
    try:
        summary = wikipedia.summary(topic, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError:
        return f"'{topic}' has multiple meanings. Please be more specific."
    except wikipedia.exceptions.PageError:
        return f"Sorry, I couldn't find information on '{topic}'."
    except Exception:
        return f"Sorry, I couldn't retrieve information on '{topic}'."