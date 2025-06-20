import random
import wikipedia
import pyjokes

facts = [
    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old!",
    "Octopuses have three hearts and blue blood.",
    "Bananas are berries, but strawberries are not.",
    "Sharks existed before trees did—over 400 million years ago!",
    "The Eiffel Tower can be 15 cm taller during the summer due to heat expansion."
]

def tell_joke():
    return pyjokes.get_joke(language='en', category='neutral')

def tell_fact():
    return random.choice(facts)

def get_knowledge(topic):
    try:
        summary = wikipedia.summary(topic, sentences=2)
        return summary
    except Exception:
        return "Sorry, I couldn't find information on that topic."
