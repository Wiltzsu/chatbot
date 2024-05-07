from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.languages import ENG
from chatterbot.trainers import ChatterBotCorpusTrainer
import hashlib
import spacy
import sqlite3

# Load Spacy model (Spacy is a software library for advanced natural language processing)
nlp = spacy.load("en_core_web_sm")

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
    ]

# Function to create a hash of conversation data
def hash_conversation(conversation):
    # Takes the list of conversation strings and concatenates them into a single string using join
    convo_string = ''.join(conversation).encode('utf-8') # Encodes the string to utf-8 which is needed because md5 function requires binary data
    return hashlib.md5(convo_string).hexdigest() # Computes the md5 hash of the encoded string. hexdigest() method returns the hash as a hexadecimal string

# Connect to the database and check for changes
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

# Main interaction loop
def main():
    print("FacilityBot: How can I help you?")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("FacilityBot: Goodbye!")
                break
            response = chatbot.get_response(user_input)
            print("FacilityBot: ", response)
        except (KeyboardInterrupt, EOFError, SystemExit):
            print("FacilityBot: Goodbye!")
            break

if __name__ == "__main__":
    main()