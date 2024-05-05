from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.languages import ENG
import spacy
import sqlite3

# Load Spacy model (Spacy is a software library for advanced natural language processing)
nlp = spacy.load("en_core_web_sm")

# Initialize ChatterBot with the correct Spacy model, adapters and configurations
chatbot = ChatBot("ChattiBotti", 
                  tagger_language=ENG,
                  storage_adapter='chatterbot.storage.SQLStorageAdapter',
                  database_uri='sqlite:///database.sqlite3',
                  logic_adapters=[
                      'chatterbot.logic.BestMatch', # Handles general queries
                      'chatterbot.logic.MathematicalEvaluation',
                      #'chatterbot.logic.TimeLogicAdapter'
                  ])

# Define a conversation array to train the chatbot
conversation = [
    "Hello",
    "Hi there!",
    "How are you?",
    "I'm doing well, thanks! How about you?",
    "I'm good, thanks for asking.",
    "Good to hear that. What can I do for you today?",
    
    "Hey",
    "Hello! How can I help you today?",
    "What's up?",
    "Not much, just here to help you! What's up with you?",
    
    "Good morning",
    "Good morning! I hope you have a great day ahead.",
    "Good evening",
    "Good evening! How was your day?",
    
    "How's it going?",
    "It's going well, thanks! And you?",
    "What are you doing?",
    "I'm here to assist you. Tell me, how can I help?",
    
    "Bye",
    "Goodbye! Have a great day ahead.",
    "See you later",
    "Sure, see you later! Don't hesitate to ask if you need more help.",
    
    "Thank you",
    "You're welcome!",
    "Thanks",
    "Anytime! Let me know if there's anything else I can do for you.",
    
    "This is great",
    "I'm glad you think so! Anything else you'd like to add?",
    "I am bored",
    "Let's change that! What do you enjoy doing?",
    
    "Tell me a joke",
    "Why don't scientists trust atoms? Because they make up everything!",
    "Can you help me?",
    "Of course! What do you need help with?"
]


# Connect to SQLite database to check for existing data
conn = sqlite3.connect('database.sqlite3')
cursor = conn.cursor()

# Check if there is already training data in the database
cursor.execute("SELECT COUNT(*) FROM statement") # Ensure that the table name exists
count = cursor.fetchone()[0]

if count == 0:
    trainer = ListTrainer(chatbot)
    trainer.train(conversation)
    print("Training completed.")
else:
    print("Chatbot has already been trained with existing data.")

conn.close()

# Main loop to interact with the chatbot

try:
    while True:
        user_input = input("You: ")
        bot_response = chatbot.get_response(user_input)
        print("ChattiBotti:", bot_response)
except (KeyboardInterrupt, EOFError, SystemExit):
    print("Chat session ended.")