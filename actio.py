import text_to_speech
import speech_to_text
import datetime
import webbrowser
import weather

def Action (data):
    user_data = data.lower()

    if "what is your name" in user_data :
        text_to_speech.text_to_speech("My name is Virtual Assistant")
        return "My name is Virtual Assistant"

    elif "hello" in user_data or "hye" in  user_data :
        text_to_speech.text_to_speech("hey , sir how can i help you")
        return "hey , sir how can i help you"

    elif "good morning" in user_data :
        text_to_speech.text_to_speech("good morning, Sir")
        return "good morning, Sir"


    elif "time now" in user_data :
        current_time = datetime.datetime.now()
        Time = (str)(current_time.hour) + "Hour :" , (str)(current_time.minute) + "Minute"
        text_to_speech.text_to_speech(Time)
        return Time

    elif "shutdown" in user_data :
        text_to_speech.text_to_speech("OK sir")
        return "OK sir"

    elif "play music" in user_data :
        webbrowser.open("https://gaana.com/")
        text_to_speech.text_to_speech("Gaana.com is now ready for u")
        return "Gaana.com is now ready for u"

    elif "open youtube" in user_data :
        webbrowser.open("https://youtube.com/")
        text_to_speech.text_to_speech("Youtube.com is now ready for u")
        return "Youtube.com is now ready for u"

    elif "open google" in user_data :
        webbrowser.open("https://google.com/")
        text_to_speech.text_to_speech("Google.com is now ready for u")
        return "Google.com is now ready for u"

    elif "weather" in user_data :
        ans = weather.weather()
        text_to_speech.text_to_speech(ans)
        return ans



    else :
        text_to_speech.text_to_speech("I am not able to understand")
        return "I am not able to understand"
