# AI Voice Chatbot

A Python Tkinter chatbot for daily conversation. You can type messages or use your microphone, and the assistant can answer open-ended questions through the Gemini API.

## Features

- Chat-style GUI built with Tkinter
- Text input and microphone input
- Text-to-speech replies
- API-backed daily conversation
- Local commands for time, weather, jokes, facts, Google, YouTube, and music
- Conversation reset with `clear chat`, `reset chat`, or the Clear button

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Set your API key before running the app.

PowerShell:

```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

Optional settings:

```powershell
$env:GEMINI_MODEL="gemini-2.0-flash"
$env:GEMINI_API_BASE="https://generativelanguage.googleapis.com/v1beta"
```

Run the chatbot:

```bash
python gui.py
```

## Example Messages

- "How was your day?"
- "Explain photosynthesis simply"
- "Give me ideas for a weekend project"
- "Tell me a joke"
- "What is the time now?"
- "Open YouTube"
- "Reset chat"
