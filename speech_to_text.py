import speech_recognition as sr

def speech_to_text():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        
        voice_data = r.recognize_google(audio)
        print(f"Recognized: {voice_data}")
        return voice_data
    except sr.WaitTimeoutError:
        print("Listening timed out")
        return ""
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Speech recognition request failed: {e}")
        return ""
    except Exception as e:
        print(f"Microphone error: {e}")
        return ""