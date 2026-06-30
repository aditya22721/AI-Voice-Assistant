from tkinter import *
from tkinter import ttk
import threading

from PIL import Image, ImageTk

import actio
import speech_to_text

root = Tk()
root.title("MediGuide - Emergency Assistant")
root.geometry("620x720")
root.config(bg="#f5f7fb")
root.minsize(520, 620)


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
    add_message("Bot", "Chat reset. I'm ready to help with your health and safety needs.")


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
    # If image not found, use a text-based icon
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
    text="Emergency First Aid & Daily Assistant",
    font=("Segoe UI", 10),
    bg="#c0392b",
    fg="#f5d6d6",
).pack(anchor=W)

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
footer = Frame(root, bg="#f5f7fb", padx=18, pady=14)  # Fixed: pady is now a single integer
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
    "Hello! I'm MediGuide - your emergency first aid assistant. 🚑\n\n"
    "I can help with:\n"
    "• Emergency situations (heart attack, choking, bleeding, burns, etc.)\n"
    "• General health questions\n"
    "• Weather updates\n"
    "• Daily conversations\n\n"
    "⚠️ Remember: For life-threatening emergencies, call 911 immediately!"
)

entry.focus()
root.mainloop()