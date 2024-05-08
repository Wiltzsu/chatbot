from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.languages import ENG
import hashlib
import spacy
import sqlite3

app = Flask(__name__)

# Initialize ChatterBot with the correct Spacy model, adapters and configurations
chatbot = ChatBot(
    "FacilityBot",  # Renamed for clarity
    tagger_language=ENG,
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///database.sqlite3',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand.',
            'maximum_similarity_threshold': 0.90
        },
        'chatterbot.logic.MathematicalEvaluation',
    ]
)

# Define a conversation array to train the chatbot in English
conversation = [
    # Add your conversation data here
]

def hash_conversation(conversation):
    convo_string = ''.join(conversation).encode('utf-8')
    return hashlib.md5(convo_string).hexdigest()

# Connect to SQLite database to check for existing data
conn = sqlite3.connect('database.sqlite3')
cursor = conn.cursor()

# Ensure the 'hashes' table exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS hashes (
    id INTEGER PRIMARY KEY,
    hash TEXT NOT NULL
);
''')

# Get the latest hash from the database
cursor.execute("SELECT hash FROM hashes ORDER BY id DESC LIMIT 1")
last_hash = cursor.fetchone()

# Calculate current hash
current_hash = hash_conversation(conversation)

# Compare hashes and train if different
if last_hash is None or last_hash[0] != current_hash:
    trainer = ListTrainer(chatbot)
    trainer.train(conversation)
    print("Training completed with updated conversation data.")
    # Update the hash in the database
    cursor.execute("INSERT INTO hashes (hash) VALUES (?)", (current_hash,))
    conn.commit()
else:
    print("No updates in conversation data. No re-training required.")

conn.close()

# Routes for Flask app
@app.route("/")
def home():
    return render_template("ui.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.form["user_input"]
    bot_response = chatbot.get_response(user_input)
    return str(bot_response)

# Starting the Flask app
if __name__ == "__main__":
    app.run(debug=True)
