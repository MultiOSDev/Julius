'''
Julius is basically Jarvis, but with a different name.
Julius is meant to be a full Artificial Intelligence, at your service able to learn, act, speak and function like jarvis. 
Julius will function with Main.py as its core memory, loading and allat other fun stuff here. Currently, because too complex, We have another file called Algorith.py that is the algorithm that is a very basic, very dirty learning algorithm. 
It wont exactly feel natural but i hope i can add that later
Julius will be able to learn, and remember things, and will be able to open programs, and do other fun stuff.

TODO:
- Make Him feel natural
- Make him learn better
'''


import speech_recognition as sr
import pyttsx3
import json
import os
import spacy
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
from bs4 import BeautifulSoup
import threading
import time
import random
import datetime
import Algorith
import duckduckgo_search 

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize speech recognition and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty("rate", 170)  # Adjust speech rate

# Memory Storage (simple JSON-based memory)
MEMORY_FILE = "Julius_memory.json"
conversation_memory = {}  # Holds the last few interactions


# Get vector representation of text
def get_vector(text):
    return nlp(text).vector
 

# Find the most similar memory entry
def fuzzy_recall(command, memory):
    command_vector = get_vector(command)
    best_match = None
    highest_similarity = -1

    for key, value in memory.items():
        key_vector = get_vector(key)
        similarity = cosine_similarity([command_vector], [key_vector])[0][0]

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = (key, value)

    return best_match


# Speak function
def speak(text):
    print(f"Julius: {text}")  # Debug output
    engine.say(text)
    engine.runAndWait()


def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}  # Return empty memory if JSON is corrupted
    return {}

def save_memory(data):
    try:
        with open(MEMORY_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print("Error saving memory:", e)



# Listen for user input
def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Calibrates background noise
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=7)  # Timeout after 5 seconds of silence
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return "Sorry, I didn't catch that."
        except sr.RequestError:
            return "Error: Could not request results."
        except sr.WaitTimeoutError:
            return "No input detected."
        

def update_conversation(topic, command, response):
    if topic not in conversation_memory:
        conversation_memory[topic] = []
    
    conversation_memory[topic].append((command, response))
    
    # Limit memory size per topic
    if len(conversation_memory[topic]) > 5:
        conversation_memory[topic].pop(0)

def get_conversation_context(topic):
    if topic in conversation_memory:
        return " ".join([f"User: {cmd[0]} | Julius: {cmd[1]}" for cmd in conversation_memory[topic]])
    return ""




# Get conversation context
def get_conversation_context():
    return " ".join([f"User: {cmd[0]} | Julius: {cmd[1]}" for cmd in conversation_history])


# Basic AI response using an external algorithm
def get_basic_ai_response(command):
    context = get_conversation_context()
    prompt = f"{context} User: {command} Julius:"
    return Algorithm.get_basic_ai_response(prompt)  # Ensure Algorithm module exists


# Determine user intent
def analyze_intent(command):
    doc = nlp(command)

    if any(word in command for word in ["search", "find", "look up"]):
        return "search"
    elif "remember" in command or "note that" in command or "remind me" in command:
        return "remember"
    elif "what do you remember about" in command:
        return "recall"
    elif "open browser" in command:
        return "open_browser"
    elif "how are you" in command:
        return "status"
    elif "exit" in command:
        return "exit"
    else:
        return "unknown"



def google_search(query):
    try:
        results = duckduckgo_search.DuckDuckGoSearch().search(query, max_results=1)
        return results[0]['body'] if results else "I couldn't find an answer."
    except Exception as e:
        return "I couldn't find an answer."

# Background tasks (e.g., reminders, updates)

def background_tasks():
    while True:
        # Julius can do passive tasks here (e.g., checking reminders)
        time.sleep(10)  # Adjust timing as needed


# Handle user commands
def handle_command(command, memory):
    intent = analyze_intent(command)

    if intent == "recall":
        key = command.replace("what do you remember about", "").strip()
        if key in memory:
            speak(f"You told me that {key} means {memory[key]}.")
        else:
            speak("I don't remember anything about that.")

    elif intent == "remember":
        key = command.replace("remember", "").strip()
        speak(f"What should I remember about {key}?")
        value = listen()
        if value:
            memory[key] = value
            save_memory(memory)
            speak(f"Got it. I will remember that {key} means {value}.")

    elif intent == "open_browser":
        speak("Opening the browser.")
        os.system("start chrome" if os.name == "nt" else "open -a 'Google Chrome'")

    elif intent == "status":
        speak("I'm functioning within normal parameters.")

    elif intent == "search":
        query = command.replace("search for", "").strip()
        result = google_search(query)
        speak(f"Here's what I found: {result}")

    elif intent == "exit":
        speak("Goodbye sir.")
        exit()

    else:
        speak("I'm not sure how to respond to that yet.")


# Main loop
memory = load_memory()
threading.Thread(target=background_tasks, daemon=True).start()

while True:
    command = listen()
    if command:
        handle_command(command, memory)
