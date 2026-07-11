# text_to_speech.py
import pyttsx3

engine = None

def text_to_speech(text):
    global engine
    try:
        if engine is None:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
        engine.say(text)
        engine.runAndWait()
    except:
        print(f"TTS: {text}")