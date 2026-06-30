"""Test the emergency assistant without GUI"""

import actio

def test_assistant():
    print("MediGuide Emergency Assistant - Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("MediGuide: Goodbye! Stay safe.")
            break
        
        response = actio.Action(user_input)
        print(f"MediGuide: {response}\n")

if __name__ == "__main__":
    test_assistant()