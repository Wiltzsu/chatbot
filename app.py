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
            'maximum_similarity_threshold': 0.80
        },
        'chatterbot.logic.MathematicalEvaluation',
    ]
)

# Define a conversation array to train the chatbot in English
conversation = [
    # Amenities Reservation
    "How do I reserve the clubhouse for a private event?",
    "You can reserve the clubhouse by contacting the management office or booking through our online portal. A refundable deposit may be required.",
    "Is there a fee to use the party room?",
    "Yes, there is a nominal fee to use the party room which covers cleaning and maintenance. You can view the rates and book the room through the management office.",
    "Can I book the tennis court in advance?",
    "Yes, the tennis courts can be booked up to one week in advance through our resident portal or at the management office.",

    # Pet Policies
    "What are the rules for walking pets in the building?",
    "Pets must be leashed at all times in public areas and you should use the designated pet relief areas for any pet waste.",
    "Are there any restrictions on the types of pets allowed?",
    "Our community allows cats and dogs, but breeds known to be aggressive are not permitted. Please check with the management office for a list of restricted breeds.",
    "Do I need to register my pet with the building?",
    "Yes, all pets must be registered with the management office. There is a one-time fee for pet registration.",

    # Vehicle Regulations
    "Where should I park my motorcycle?",
    "Motorcycles should be parked in the designated two-wheeler parking spaces located in the garage.",
    "What is the policy for visitor parking?",
    "Visitor parking is available on a first-come, first-served basis and visitors must register their vehicle with the concierge upon arrival.",
    "Can I wash my car in the parking lot?",
    "Vehicle washing is not permitted in the parking lot to prevent pollutants from entering storm drains. We recommend using a professional car wash service.",

    # Tenant Communications
    "How can I receive updates about building maintenance?",
    "Updates about scheduled maintenance and other important notices are sent via email and posted on the resident portal. Please ensure your contact information is up to date.",
    "What is the best way to communicate with my property manager?",
    "You can reach your property manager by email, phone, or through the resident portal for non-emergency queries. For emergencies, please use the emergency contact number provided.",
    "Can I subscribe to receive SMS alerts about emergencies?",
    "Yes, you can subscribe to SMS alerts by updating your communication preferences in your resident profile on our portal.",

    # Compliance and Safety
    "What should I do if I see someone smoking in non-smoking areas?",
    "Please report any violations of the smoking policy to the management office. We appreciate your cooperation in keeping our community safe and clean.",
    "Are fire drills conducted in the building?",
    "Yes, fire drills are conducted annually to ensure residents are familiar with evacuation procedures. You will be notified in advance about the schedule.",
    "What are the quiet hours in the building?",
    "Quiet hours are from 10 PM to 7 AM on weekdays and from 11 PM to 8 AM on weekends and holidays.",

    # Building Policies
    "Can I install a satellite dish on my balcony?",
    "Satellite dishes are not permitted on balconies due to safety and aesthetic reasons. We provide a central satellite service that you can connect to.",
    "What is the policy on hanging decorations on the front door?",
    "Small decorations like wreaths are allowed, but they should not damage the door or disrupt the building's aesthetic. Please ensure decorations are secured properly.",
    "Are residents allowed to host events in the common areas?",
    "Residents can host events in designated common areas with prior approval from the management office. A reservation may require a security deposit."
    
>>>>>>> ba1b18cdf4f666624d12b03f7661a0acb1ee2e66
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
