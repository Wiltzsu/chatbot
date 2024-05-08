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
