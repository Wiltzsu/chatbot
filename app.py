from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.languages import ENG
import spacy
import sqlite3

app = Flask(__name__)

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
    
    "Hey there!",
    "Hello! How can I assist you today?",
    "What's cracking?",
    "Not much, just ready to help you out! How about you?",

    "Morning!",
    "Good morning! How's your day starting off?",
    "Evening!",
    "Good evening! What's on your mind?",

    "Howdy!",
    "Hey! What can I do for you?",
    "What's happening?",
    "Just here, at your service! What can I help you with?",

    "See ya!",
    "Take care! Let me know if you need anything else.",
    "Later!",
    "Until next time! Feel free to reach out whenever.",

    "Cheers!",
    "You're welcome!",
    "Thanks a bunch!",
    "Anytime! Don't hesitate to ask if you need more assistance.",

    "Nice!",
    "Glad you think so! What else can I do for you?",
    "Boredom alert!",
    "Let's shake things up! What interests you?",

    "Hit me with a joke!",
    "Why don't skeletons fight each other? They don't have the guts!",
    "Need a laugh?",
    "Sure thing! Why did the scarecrow win an award? Because he was outstanding in his field!",

    "Can you assist me?",
    "Absolutely! What do you need help with?",
    "I'm stuck, help!",
    "No problem! Let's work through it together."
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

@app.route("/")
def home():
    return render_template("ui.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.form["user_input"]
    bot_response = chatbot.get_response(user_input)
    return str(bot_response)

if __name__ == "__main__":
    app.run(debug=True)
