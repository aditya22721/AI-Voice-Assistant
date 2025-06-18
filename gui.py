from tkinter import *
from PIL import Image, ImageTk
import speech_to_text
import actio

root = Tk()
root.title("AI Assistant")
root.geometry("550x675")
root.config(bg="#54F1A0")  # Valid hex color (example)
# ask fun

def ask ():
    user_val = speech_to_text.speech_to_text()
    bot_val = actio.Action(user_val)
    text.insert(END , 'user--->' + user_val+"\n")
    if bot_val != None:
        text.insert(END , "Bot <---"+str(bot_val)+"\n")
    if bot_val == "OK sir":
        root.destroy()


#send 

def send ():
    send = entry.get()
    bot = actio.Action(send)
    text.insert(END , 'user--->' + send+"\n")
    if bot != None:
        text.insert(END , "Bot <---"+str(bot)+"\n")
    if bot == "OK sir":
        root.destroy()



#delete

def del_text ():
    text.delete('1.0', "end")


# Frames
frame = LabelFrame(root, padx=20, pady=10, borderwidth=3, relief="raised", bg="#D2EF83")
frame.pack(pady=10)  # Using pack instead of grid for better alignment

# Text label
text_label = Label(frame, text="AI Assistant", font=("comic sans ms", 14, "bold"), bg="#DDE08F", fg="white")
text_label.pack(pady=5)

# Load and resize image
image = Image.open("download (1).jpg")
image = image.resize((150, 150))  # Adjust size as needed
image = ImageTk.PhotoImage(image)

# Display resized image
image_label = Label(frame, image=image)
image_label.image = image  # Prevent garbage collection
image_label.pack(pady=5)

# Adding a text widget
text = Text(root, font=('courier 10 bold'), bg="#92BEEB", fg="white", wrap=WORD)
text.place(x=100, y=375, width=375, height=100)

#entry widget

entry = Entry(root , justify=CENTER)
entry.place(x=100, y=500 , width =350 , height=30)

#button 1

Button1 = Button(root,text="ASK" , bg="#357CCD" , pady=16 , padx=40 , borderwidth=3 , relief=SOLID,command=ask)
Button1.place(x=70, y=575)

#button2

Button2 = Button(root,text="SEND" , bg="#357CCD" , pady=16 , padx=40 , borderwidth=3 , relief=SOLID,command=send)
Button2.place(x=400, y=575)

#button3

Button3 = Button(root,text="DELETE" , bg="#357CCD" , pady=16 , padx=40 , borderwidth=3 , relief=SOLID,command=del_text)
Button3.place(x=225, y=575)



root.mainloop()