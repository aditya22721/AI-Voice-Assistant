import pyttsx3


def text_to_speech(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', max(120, rate - 70))
    engine.say(text)
    engine.runAndWait()

