# gui.py (Updated with better location handling)
from tkinter import *
from tkinter import ttk
import threading
import geocoder
from dotenv import load_dotenv

load_dotenv()

from PIL import Image, ImageTk

import actio
import speech_to_text

root = Tk()
root.title("MediGuide - Smart Assistant")
root.geometry("620x720")
root.config(bg="#f5f7fb")
root.minsize(520, 620)

current_location = None
location_update_counter = 0

def get_location():
    """Enhanced location detection with multiple methods"""
    try:
        # Method 1: IP-based location
        g = geocoder.ip('me')
        if g.latlng:
            return {
                'lat': g.latlng[0],
                'lng': g.latlng[1],
                'address': g.address,
                'city': g.city,
                'state': g.state,
                'country': g.country
            }
    except:
        pass
    
    # Method 2: Try with ipapi.co directly
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('latitude') and data.get('longitude'):
                return {
                    'lat': data.get('latitude'),
                    'lng': data.get('longitude'),
                    'address': f"{data.get('city')}, {data.get('country_name')}",
                    'city': data.get('city'),
                    'state': data.get('region'),
                    'country': data.get('country_name')
                }
    except:
        pass
    
    return None

def update_location_display():
    """Update location display with better error handling"""
    global location_update_counter
    location_update_counter += 1
    
    location = get_location()
    if location:
        city = location.get('city', 'Unknown')
        country = location.get('country', '')
        if city and country:
            location_var.set(f"📍 {city}, {country}")
        elif city:
            location_var.set(f"📍 {city}")
        else:
            location_var.set("📍 Location detected")
    else:
        if location_update_counter < 3:
            location_var.set("📍 Detecting location...")
        else:
            location_var.set("📍 Location unavailable")
    
    # Update every 30 seconds, but stop after 3 attempts if failed
    if location_update_counter < 5:
        root.after(30000, update_location_display)

def add_message(sender, message):
    chat_box.config(state=NORMAL)
    if sender == "Bot":
        chat_box.insert(END, f"🤖 {message}\n\n")
    else:
        chat_box.insert(END, f"👤 {message}\n\n")
    chat_box.see(END)
    chat_box.config(state=DISABLED)

def set_busy(is_busy):
    state = DISABLED if is_busy else NORMAL
    send_button.config(state=state)
    ask_button.config(state=state)
    entry.config(state=state)
    status_var.set("Thinking..." if is_busy else "Ready")

def handle_bot_response(user_message):
    try:
        bot_message = actio.Action(user_message)
        if bot_message:
            root.after(0, add_message, "Bot", str(bot_message))
            if "goodbye" in str(bot_message).lower():
                root.after(500, root.destroy)
    except Exception as e:
        root.after(0, add_message, "Bot", f"Sorry, I encountered an error: {e}")
    finally:
        root.after(0, set_busy, False)

def send_message(event=None):
    user_message = entry.get().strip()
    if not user_message:
        return

    entry.delete(0, END)
    add_message("You", user_message)
    set_busy(True)
    threading.Thread(target=handle_bot_response, args=(user_message,), daemon=True).start()

def ask_voice():
    set_busy(True)

    def listen_and_send():
        try:
            user_message = speech_to_text.speech_to_text()
            if user_message:
                root.after(0, add_message, "You", user_message)
                handle_bot_response(user_message)
            else:
                root.after(0, add_message, "Bot", "I did not catch that. Please try again.")
        except Exception as e:
            root.after(0, add_message, "Bot", f"Voice error: {e}")
        finally:
            root.after(0, set_busy, False)

    threading.Thread(target=listen_and_send, daemon=True).start()

def clear_chat():
    chat_box.config(state=NORMAL)
    chat_box.delete("1.0", END)
    chat_box.config(state=DISABLED)
    actio.reset_conversation()
    add_message("Bot", "Chat reset. I'm ready to help with any topic!")

# Header Section
header = Frame(root, bg="#c0392b", padx=18, pady=14)
header.pack(fill=X)

try:
    image = Image.open("download (1).jpg")
    image = image.resize((58, 58))
    avatar = ImageTk.PhotoImage(image)
    image_label = Label(header, image=avatar, bg="#c0392b")
    image_label.image = avatar
    image_label.pack(side=LEFT, padx=(0, 12))
except Exception:
    Label(
        header,
        text="🚑",
        font=("Segoe UI", 40),
        bg="#c0392b",
        fg="#ffffff"
    ).pack(side=LEFT, padx=(0, 12))

title_area = Frame(header, bg="#c0392b")
title_area.pack(side=LEFT, fill=X, expand=True)

Label(
    title_area,
    text="🚑 MediGuide",
    font=("Segoe UI", 18, "bold"),
    bg="#c0392b",
    fg="#ffffff",
).pack(anchor=W)

Label(
    title_area,
    text="Your Intelligent Assistant - Powered by Free APIs",
    font=("Segoe UI", 10),
    bg="#c0392b",
    fg="#f5d6d6",
).pack(anchor=W)

# Location Display
location_frame = Frame(root, bg="#e8f0fe", padx=10, pady=3)
location_frame.pack(fill=X)

location_var = StringVar(value="📍 Detecting location...")
Label(
    location_frame,
    textvariable=location_var,
    font=("Segoe UI", 9),
    bg="#e8f0fe",
    fg="#1a73e8",
).pack(side=LEFT)

# API Status Display
api_status_frame = Frame(root, bg="#e8f0fe", padx=10, pady=3)
api_status_frame.pack(fill=X)

import os
api_type = os.getenv("USE_API", "huggingface").upper()
api_status = f"🔌 API: {api_type} (FREE)"
Label(
    api_status_frame,
    text=api_status,
    font=("Segoe UI", 8),
    bg="#e8f0fe",
    fg="#2e7d32",
).pack(side=LEFT)

# Emergency Warning Label
warning_frame = Frame(root, bg="#fef3e2", padx=10, pady=5)
warning_frame.pack(fill=X)

Label(
    warning_frame,
    text="⚠️ FOR EMERGENCIES: Call 911/112/999 immediately",
    font=("Segoe UI", 10, "bold"),
    bg="#fef3e2",
    fg="#c0392b",
).pack()

# Quick Action Buttons
quick_buttons = Frame(root, bg="#f5f7fb", padx=10, pady=5)
quick_buttons.pack(fill=X)

Button(
    quick_buttons,
    text="🏥 Find Hospitals",
    command=lambda: send_message_quick("find hospital"),
    bg="#2ecc71",
    fg="white",
    font=("Segoe UI", 9, "bold"),
    relief=FLAT,
    padx=10,
    pady=5
).pack(side=LEFT, padx=5)

Button(
    quick_buttons,
    text="🚨 Emergency Help",
    command=lambda: send_message_quick("I need help! This is an emergency!"),
    bg="#e74c3c",
    fg="white",
    font=("Segoe UI", 9, "bold"),
    relief=FLAT,
    padx=10,
    pady=5
).pack(side=LEFT, padx=5)

Button(
    quick_buttons,
    text="🌤️ Weather",
    command=lambda: send_message_quick("weather"),
    bg="#3498db",
    fg="white",
    font=("Segoe UI", 9, "bold"),
    relief=FLAT,
    padx=10,
    pady=5
).pack(side=LEFT, padx=5)

def send_message_quick(text):
    entry.delete(0, END)
    entry.insert(0, text)
    send_message()

# Chat Frame
chat_frame = Frame(root, bg="#f5f7fb", padx=18, pady=18)
chat_frame.pack(fill=BOTH, expand=True)

chat_box = Text(
    chat_frame,
    font=("Segoe UI", 11),
    bg="#ffffff",
    fg="#18202f",
    wrap=WORD,
    relief=FLAT,
    padx=14,
    pady=14,
)
chat_box.pack(side=LEFT, fill=BOTH, expand=True)
chat_box.config(state=DISABLED)

scrollbar = ttk.Scrollbar(chat_frame, command=chat_box.yview)
scrollbar.pack(side=RIGHT, fill=Y)
chat_box.config(yscrollcommand=scrollbar.set)

# Input Frame
input_frame = Frame(root, bg="#f5f7fb", padx=18, pady=12)
input_frame.pack(fill=X)

entry = Entry(input_frame, font=("Segoe UI", 12), relief=SOLID, borderwidth=1)
entry.pack(side=LEFT, fill=X, expand=True, ipady=9)
entry.bind("<Return>", send_message)

send_button = Button(
    input_frame,
    text="Send",
    command=send_message,
    bg="#c0392b",
    fg="#ffffff",
    activebackground="#a93226",
    activeforeground="#ffffff",
    relief=FLAT,
    padx=18,
    pady=10,
)
send_button.pack(side=LEFT, padx=(10, 0))

ask_button = Button(
    input_frame,
    text="🎤 Speak",
    command=ask_voice,
    bg="#2980b9",
    fg="#ffffff",
    activebackground="#21618c",
    activeforeground="#ffffff",
    relief=FLAT,
    padx=18,
    pady=10,
)
ask_button.pack(side=LEFT, padx=(8, 0))

# Footer
footer = Frame(root, bg="#f5f7fb", padx=18, pady=14)
footer.pack(fill=X)

clear_button = Button(
    footer,
    text="Clear Chat",
    command=clear_chat,
    bg="#e7ebf3",
    fg="#18202f",
    activebackground="#d7deeb",
    relief=FLAT,
    padx=14,
    pady=8,
)
clear_button.pack(side=LEFT)

status_var = StringVar(value="Ready")
Label(
    footer,
    textvariable=status_var,
    font=("Segoe UI", 10),
    bg="#f5f7fb",
    fg="#596579",
).pack(side=RIGHT)

# Initial message
add_message(
    "Bot",
    "Hello! I'm MediGuide - your intelligent assistant. 🚑\n\n"
    "🌟 I can answer ANY question you have - FOR FREE!\n"
    "• Ask me about science, history, technology, health, relationships\n"
    "• Get weather updates, jokes, facts\n"
    "• Find nearby hospitals and emergency services\n"
    "• Get first aid guidance for emergencies\n\n"
    "🆘 Emergency Detection: I automatically detect emergencies\n"
    "and switch to emergency mode with location-based help.\n\n"
    "💡 Try asking me ANYTHING:\n"
    "• 'What is the capital of France?'\n"
    "• 'Tell me about black holes'\n"
    "• 'How to make pasta?'\n"
    "• 'I have chest pain' (Emergency mode)\n"
    "• 'find hospital' (Location service)\n\n"
    "⚠️ For life-threatening emergencies, always call 911 first!"
)

# Start location update
update_location_display()
entry.focus()
root.mainloop()