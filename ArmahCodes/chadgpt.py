import asyncio
import os
import time
import random
from datetime import datetime
import playsound
import edge_tts
import pyobject
from pyobject import *
from gradio_client import Client

class ChatBot:
    def __init__(self, model_name, history_file='conversation_history.txt'):
        self.client = Client(model_name)
        self.history_file = history_file
        self.conversation_history = self.load_history()  # Load history from file
        self.greet_user()  # Greet the user at the start

    def load_history(self):
        """Load conversation history from a file."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as file:
                return [line.strip() for line in file.readlines()]  # Read and strip lines
        return []  # Return empty list if no history file exists

    def save_history(self):
        """Save conversation history to a file."""
        with open(self.history_file, 'w') as file:
            for line in self.conversation_history:
                file.write(line + '\n')  # Write each line to the file

    def generate_system_prompt(self):
        """Generates a system prompt based on conversation history."""
        conversation = " ".join(self.conversation_history[-10:])  # Keep only the last 10 exchanges
        system_prompt = f"Conversation so far: {conversation}"
        return system_prompt

    async def text_to_speech(self, text):
        """Convert text to speech using edge_tts and play it."""
        # Create a unique audio file name using the current timestamp
        audio_file = f"response_{int(time.time())}.mp3"
        
        # Initialize the communicator with the Aria voice
        communicate = edge_tts.Communicate(text, voice="en-US-AvaMultilingualNeural")  # Using Aria voice
        await communicate.save(audio_file)  # Save the speech to an audio file
        
        # Play the audio file
        playsound.playsound(audio_file)

    async def predict(self, message, max_new_tokens=1024, temperature=0.6):
        """Send a message to the model and get the prediction (response)."""
        self.conversation_history.append(f"You: {message}")  # Append user message to history
        
        # Generate system prompt based on conversation history
        system_prompt = self.generate_system_prompt()

        result = self.client.predict(
            message=message,
            system_prompt=system_prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            api_name="/chat"
        )

        # Clean response: remove 'assistant', trim spaces
        cleaned_result = result.replace("assistant", "").strip()
        self.conversation_history.append(f"ChadGPT: {cleaned_result}")  # Append cleaned response
        
        # Save updated history to the file after each message
        self.save_history()

        # Return the cleaned response first
        return cleaned_result  # Return the cleaned response

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        self.save_history()  # Save the cleared history

    def greet_user(self):
        """Print a greeting message based on the time of day with a random emoji."""
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting = "Good morning"
        elif current_hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        emoji = random.choice(["😊", "🌟", "🚀", "🎉", "😄", "🤖", "✨"])
        greeting_message = f"{greeting}, Armaan! {emoji}"
        self.slow_print(greeting_message)

    def slow_print(self, message, delay=0.1):
        """Prints a message slowly."""
        for char in message:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()  # New line after the message

# Example usage
async def main():
    chatbot = ChatBot("chuanli11/Chat-Llama-3.2-3B-Instruct-uncensored")

    # Chat with the bot
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        elif user_input.lower() == "clear":
            chatbot.clear_history()
            print("Conversation history cleared.")
        else:
            response = await chatbot.predict(user_input)
            print(f"ChadGPT: {response}")  # Output the response first
            
            # Play the audio response after printing
            await chatbot.text_to_speech(response)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
