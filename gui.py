# gui.py - COMPLETELY FIXED with visible input box
from tkinter import *
from tkinter import ttk
import threading
import geocoder
import os
import requests
from dotenv import load_dotenv

load_dotenv()

import actio
import speech_to_text

root = Tk()
root.title("MediGuide - Smart Assistant")
root.geometry("1000x900")
root.config(bg="#f0f2f5")
root.minsize(900, 750)

# ===== LOCATION FUNCTIONS =====
location_update_counter = 0

def get_location():
    try:
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
    
    if location_update_counter < 5:
        root.after(30000, update_location_display)

# ===== CHAT FUNCTIONS =====
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
    voice_button.config(state=state)
    entry.config(state=state)
    status_var.set("🤔 Thinking..." if is_busy else "✅ Ready")

def handle_bot_response(user_message):
    try:
        bot_message = actio.Action(user_message)
        if bot_message:
            root.after(0, add_message, "Bot", str(bot_message))
            if "goodbye" in str(bot_message).lower():
                root.after(500, root.destroy)
    except Exception as e:
        root.after(0, add_message, "Bot", f"❌ Error: {e}")
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
                root.after(0, add_message, "Bot", "🎤 I didn't catch that. Please try again.")
        except Exception as e:
            root.after(0, add_message, "Bot", f"🎤 Voice error: {e}")
        finally:
            root.after(0, set_busy, False)

    threading.Thread(target=listen_and_send, daemon=True).start()

def clear_chat():
    chat_box.config(state=NORMAL)
    chat_box.delete("1.0", END)
    chat_box.config(state=DISABLED)
    actio.reset_conversation()
    add_message("Bot", "🗑️ Chat cleared! Ready to help with anything.")

def quick_action(text):
    entry.delete(0, END)
    entry.insert(0, text)
    send_message()

# ============================================
# CREATE MAIN CONTAINER WITH GRID LAYOUT
# ============================================
root.grid_rowconfigure(0, weight=0)  # Header
root.grid_rowconfigure(1, weight=0)  # Status
root.grid_rowconfigure(2, weight=0)  # Warning
root.grid_rowconfigure(3, weight=0)  # Quick buttons
root.grid_rowconfigure(4, weight=1)  # Chat (expands)
root.grid_rowconfigure(5, weight=0)  # Input (fixed height)
root.grid_rowconfigure(6, weight=0)  # Footer
root.grid_columnconfigure(0, weight=1)

# ============================================
# UI - TOP HEADER (Row 0)
# ============================================
header = Frame(root, bg="#1a237e", padx=20, pady=15)
header.grid(row=0, column=0, sticky="ew")

Label(
    header,
    text="🚑 MediGuide",
    font=("Segoe UI", 26, "bold"),
    bg="#1a237e",
    fg="#ffffff"
).pack(side=LEFT)

Label(
    header,
    text="Your Intelligent Assistant",
    font=("Segoe UI", 14),
    bg="#1a237e",
    fg="#90caf9"
).pack(side=LEFT, padx=(10, 0))

# ============================================
# UI - STATUS BAR (Row 1)
# ============================================
status_bar = Frame(root, bg="#e8eaf6", padx=15, pady=5)
status_bar.grid(row=1, column=0, sticky="ew")

location_var = StringVar(value="📍 Detecting location...")
Label(
    status_bar,
    textvariable=location_var,
    font=("Segoe UI", 10),
    bg="#e8eaf6",
    fg="#1a237e"
).pack(side=LEFT)

hf_status = "✅" if os.getenv("HF_API_KEY") and os.getenv("HF_API_KEY") != "your_huggingface_token_here" else "❌"
email_status = "✅" if os.getenv("ALERT_EMAIL") and os.getenv("ALERT_PASSWORD") else "❌"
api_status = f"🤖 AI: {hf_status}  📧 Gmail: {email_status}"
Label(
    status_bar,
    text=api_status,
    font=("Segoe UI", 10),
    bg="#e8eaf6",
    fg="#1a237e"
).pack(side=RIGHT)

# ============================================
# UI - EMERGENCY WARNING (Row 2)
# ============================================
warning_frame = Frame(root, bg="#ffebee", padx=15, pady=6)
warning_frame.grid(row=2, column=0, sticky="ew")

Label(
    warning_frame,
    text="⚠️ FOR LIFE-THREATENING EMERGENCIES: Call 911 / 112 / 999 immediately",
    font=("Segoe UI", 11, "bold"),
    bg="#ffebee",
    fg="#c62828"
).pack()

# ============================================
# UI - QUICK ACTION BUTTONS (Row 3)
# ============================================
quick_frame = Frame(root, bg="#f5f5f5", padx=15, pady=10)
quick_frame.grid(row=3, column=0, sticky="ew")

buttons = [
    ("🏥 Find Hospitals", "#2e7d32", "find hospital"),
    ("🚨 Emergency Help", "#c62828", "I need help! This is a medical emergency!"),
    ("🌤️ Weather", "#0d47a1", "weather"),
    ("😂 Joke", "#6a1b9a", "tell me a joke"),
    ("📚 Fact", "#e65100", "tell me a fact"),
]

for text, color, cmd in buttons:
    Button(
        quick_frame,
        text=text,
        command=lambda c=cmd: quick_action(c),
        bg=color,
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief=FLAT,
        padx=15,
        pady=8,
        cursor="hand2"
    ).pack(side=LEFT, padx=5)

# ============================================
# UI - CHAT DISPLAY (Row 4 - Expands)
# ============================================
chat_frame = Frame(root, bg="#f5f5f5", padx=15, pady=15)
chat_frame.grid(row=4, column=0, sticky="nsew")

chat_box = Text(
    chat_frame,
    font=("Segoe UI", 12),
    bg="#ffffff",
    fg="#1a1a1a",
    wrap=WORD,
    relief=FLAT,
    padx=20,
    pady=20,
    borderwidth=0,
    highlightthickness=1,
    highlightcolor="#d0d0d0"
)
chat_box.pack(side=LEFT, fill=BOTH, expand=True)
chat_box.config(state=DISABLED)

scrollbar = ttk.Scrollbar(chat_frame, command=chat_box.yview)
scrollbar.pack(side=RIGHT, fill=Y)
chat_box.config(yscrollcommand=scrollbar.set)

# ============================================
# UI - INPUT AREA (Row 5 - FIXED HEIGHT)
# ============================================
input_frame = Frame(root, bg="#ffffff", padx=20, pady=12, height=100)
input_frame.grid(row=5, column=0, sticky="ew")
input_frame.grid_propagate(False)  # Prevent shrinking

# Input row
input_row = Frame(input_frame, bg="#ffffff")
input_row.pack(fill=X)

# ===== MESSAGE INPUT BOX (Using Entry for single line) =====
entry = Entry(
    input_row,
    font=("Segoe UI", 15),
    relief=SOLID,
    borderwidth=2,
    bg="#fafafa",
    fg="#1a1a1a",
    highlightthickness=2,
    highlightcolor="#1a237e",
    highlightbackground="#d0d0d0"
)
entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10), ipady=12)
entry.bind("<Return>", send_message)
entry.focus_set()

def on_focus_in(e):
    entry.config(bg="#ffffff", highlightbackground="#1a237e")
def on_focus_out(e):
    entry.config(bg="#fafafa", highlightbackground="#d0d0d0")

entry.bind("<FocusIn>", on_focus_in)
entry.bind("<FocusOut>", on_focus_out)

# ===== SEND BUTTON =====
send_button = Button(
    input_row,
    text="Send",
    command=send_message,
    bg="#1a237e",
    fg="#ffffff",
    activebackground="#0d47a1",
    activeforeground="#ffffff",
    relief=FLAT,
    padx=28,
    pady=14,
    font=("Segoe UI", 13, "bold"),
    cursor="hand2"
)
send_button.pack(side=LEFT, padx=(0, 8))

# ===== SPEAK BUTTON =====
voice_button = Button(
    input_row,
    text="Speak",
    command=ask_voice,
    bg="#00695c",
    fg="#ffffff",
    activebackground="#004d40",
    activeforeground="#ffffff",
    relief=FLAT,
    padx=22,
    pady=14,
    font=("Segoe UI", 13, "bold"),
    cursor="hand2"
)
voice_button.pack(side=LEFT)

# Hint label
Label(
    input_frame,
    text="💡 Type your question and press Enter, or click Speak to use voice",
    font=("Segoe UI", 10),
    bg="#ffffff",
    fg="#888888",
    pady=4,
    anchor=W
).pack(fill=X)

# ============================================
# UI - FOOTER (Row 6)
# ============================================
footer = Frame(root, bg="#f5f5f5", padx=15, pady=10)
footer.grid(row=6, column=0, sticky="ew")

Button(
    footer,
    text="🗑️ Clear Chat",
    command=clear_chat,
    bg="#e0e0e0",
    fg="#333333",
    activebackground="#bdbdbd",
    relief=FLAT,
    padx=20,
    pady=10,
    font=("Segoe UI", 10),
    cursor="hand2"
).pack(side=LEFT)

status_var = StringVar(value="✅ Ready")
Label(
    footer,
    textvariable=status_var,
    font=("Segoe UI", 11),
    bg="#f5f5f5",
    fg="#555555"
).pack(side=RIGHT)

# ============================================
# INITIAL WELCOME MESSAGE
# ============================================
add_message(
    "Bot",
    "👋 Hello! I'm MediGuide, your intelligent assistant.\n\n"
    "📌 I can answer ANY question you have!\n"
    "• Ask me about science, history, technology, health, relationships\n"
    "• Get weather updates, jokes, facts\n"
    "• Find nearby hospitals and emergency services\n"
    "• Get first aid guidance for emergencies\n\n"
    "🆘 Emergency Detection: I automatically detect emergencies\n"
    "and switch to emergency mode with location-based help.\n\n"
    "💡 Try asking me anything like:\n"
    "• 'What is the capital of France?'\n"
    "• 'Tell me about black holes'\n"
    "• 'How to make pasta?'\n"
    "• 'I have chest pain!' (Emergency mode)\n"
    "• 'find hospital' (Location service)\n\n"
    "⚠️ For life-threatening emergencies, always call 911 first!"
)

# ============================================
# START
# ============================================
update_location_display()
entry.focus()
root.mainloop()