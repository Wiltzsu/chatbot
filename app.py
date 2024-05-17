from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.languages import ENG
import hashlib
import spacy
import sqlite3
from pathlib import Path

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
            'default_response': 'I am sorry, but I am not trained to answer that question.',
            'maximum_similarity_threshold': 0.80
        },
        'chatterbot.logic.MathematicalEvaluation',
    ]
)

# Define a conversation array to train the chatbot in English
conversation = [
<<<<<<< Updated upstream
    
=======
    # Tenant Services
    "How can I request a cleaning service for my apartment?",
    "You can request cleaning services through our resident portal or by contacting the management office directly. Fees and scheduling details are available online.",
    "Is there a charge for the parcel holding service?",
    "No, our parcel holding service is complimentary for all residents. Parcels can be collected from the concierge desk.",
    "What amenities are included for residents?",
    "Residents have access to the fitness center, pool, business center, and communal lounges. All amenities are included in your residency without additional charges.",

    # Building Rules
    "Are there specific rules for balcony usage?",
    "Balconies must be kept clean and free of storage items. Decorations are allowed but should not obstruct views or drip water onto balconies below.",
    "What is the policy on holiday decorations in common areas?",
    "Holiday decorations in common areas are provided by the building management. Personal decorations should be confined to your apartment's interior.",
    "Can I post notices in the elevator?",
    "Posting notices in the elevator or any common area requires prior approval from the management to ensure content and placement are appropriate.",

    # Parking Regulations
    "How do I apply for a reserved parking spot?",
    "Reserved parking spots can be applied for via the resident portal or at the management office. Availability and pricing details are provided upon request.",
    "What should I do if my parking permit is lost?",
    "Report a lost parking permit to the management office immediately to prevent misuse and to issue a new permit. A replacement fee may apply.",
    "Can visitors park overnight?",
    "Visitors can park overnight if they display a temporary parking pass, which can be obtained from the concierge or management office.",

    # Apartment Maintenance Issues
    "My ceiling fan has stopped working, what should I do?",
    "Please check if the fan's switch is in the correct position and test other controls. If it still doesn't work, submit a maintenance request for repair.",
    "Who is responsible for replacing light bulbs?",
    "Tenants are responsible for replacing light bulbs in their apartments. If you require assistance or have a hard-to-reach light, our maintenance team can help at no extra charge.",
    "The water in my shower doesn't get hot, what could be the issue?",
    "It's possible there could be an issue with your apartment's water heater settings or a malfunction. Please submit a maintenance request to have it inspected.",

    # Emergency Procedures
    "What is the evacuation plan for my floor?",
    "Evacuation plans are posted on the back of your apartment door and at the ends of each hallway. Please review them and familiarize yourself with the nearest exits.",
    "Who do I contact in case of a gas leak?",
    "In case of a gas leak, evacuate your apartment immediately and contact emergency services. After ensuring safety, notify the building management.",
    "What do I do if I smell smoke in the building?",
    "If you smell smoke, call emergency services and notify building management immediately. Use the nearest stairwell to evacuate if necessary.",

    # New Tenant Information
    "What do I need to do before moving in?",
    "Before moving in, please ensure all required documents are submitted, and fees paid. Schedule a move-in inspection and pick up your keys from the management office.",
    "Can I move in on a weekend?",
    "Weekend move-ins are possible but need to be coordinated with the management office to ensure staff availability and elevator access.",

    # General Inquiries
    "How do I subscribe to building notifications?",
    "You can subscribe to building notifications through the resident portal. Ensure your contact information is current to receive all updates.",
    "Where are the recycling facilities located?",
    "Recycling facilities are located on the basement level. There are clearly marked bins for different types of recyclable materials.",
    "Is the building pet-friendly?",
    "Yes, our building is pet-friendly. Please refer to the pet policy for details on restrictions and required deposits.",
>>>>>>> Stashed changes
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
    bot_response = str(chatbot.get_response(user_input))

    # Get the default response from the chatbot object
    default_response = 'I am sorry, but I am not trained to answer that question.'

    # If the bot's response matches the default response, save the question to a text file
    if bot_response == default_response:
        save_unanswered_question(user_input)

    return str(bot_response)

def save_unanswered_question(question):
    script_directory = Path(__file__).resolve().parent
    filename = script_directory / "unanswered_questions.txt"
    try:
        with open(filename, "a") as file:
            file.write(question + "\n")
        print(f"Unanswered question saved to {filename}")
    except Exception as e:
        print(f"Error occurred while saving unanswered question: {e}")


# Starting the Flask app
if __name__ == "__main__":
    app.run(debug=True)
