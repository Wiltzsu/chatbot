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
# Heating conversations
# Coversation 1
    "Hi, I'm having trouble with my heating.",
    "I'm sorry to hear that. Can you tell me more about what's happening with your heating?",
    "My radiator is not heating up at all.",
    "I understand. Could you please tell me your apartment number?",
    "My apartment number is 21.",
    "Thank you for the information. I will send a maintenance person to check your radiator as soon as possible.",
    "How long will the repair take?",
    "The maintenance person should arrive within the hour, and we will assess the duration of the repair based on the situation.",
    "Can I leave my keys with the neighbor? I won't be home.",
    "Yes, you can. Please provide us with your neighbor's contact details so we can coordinate with them.",
    
# Water leak conversations
# Conversation 1
	"Is a water leak an emergency?",
	"Yes, a water leak is always considered an emergency. Please shut off the main water valve and inform us immediately.",
	"The faucet in the bathroom is leaking. What should I do?",
	"First, shut off the main water valve to stop the water flow, and inform us about the problem. We will send maintenance to your location as quickly as possible.",
    
# Conversation 2
	"I just noticed a puddle of water under my kitchen sink. What should I do?",
	"It sounds like you might have a leak. Please check if the water valves under the sink can be turned off to stop the leak temporarily and then describe any visible damage or signs of leakage.",
	"The pipes are dripping, and there's rust around the connections.",
	"Thank you for checking. I recommend keeping the valve closed and using a bucket to catch any drips. A maintenance team member will be dispatched to your location soon to fix the issue.",

# Conversation 3
	"There's water coming from my ceiling. I think there's a leak from the apartment above.",
	"That's concerning. Have you been able to contact the resident above you?",
	"No, there's no response from their apartment.",
	"I'll notify building management and send someone to check both your apartment and the unit above. Please move any valuables away from the affected area to prevent water damage.",
	
# Conversation 4
	"How do I report a water leak in the public hallway?",
	"Thank you for bringing this to our attention. Can you specify which floor the leak is on?",
	"It's on the second floor near the stairwell.",
	"I've informed maintenance to address the leak immediately. We appreciate your help in keeping the building safe and clean.",
	
# Conversation 5
	"What should I do if I suspect a water leak behind a wall? I can hear dripping sounds.",
	"It's important to address hidden leaks promptly to avoid structural damage. Can you tell if the sound is localized to one area?",
	"Yes, it's most noticeable behind the bathroom wall.",
	"Please avoid using the bathroom if possible, and I will send a specialist to inspect and repair the leak as soon as possible.",
			 
# Maintenance conversations
# Cancel maintenance
    "How do I cancel a maintenance request?",
    "You can cancel a maintenance request by calling our customer service or sending an email. We will need your apartment number to proceed with the cancellation.",
  
 # Update maintenance
    "I would like to update my maintenance request information.",
    "How would you like to update your request? You can send the updated information by email or call our customer service.",
    
 # Refridgerator
    "My refrigerator isn't working, what should I do?",
    "Please inform us about the model of your refrigerator and describe the problem in more detail. We will send a technician to check the situation."
]

# Function to create a hash of conversation data
def hash_conversation(conversation):
    convo_string = ''.join(conversation).encode('utf-8')
    return hashlib.md5(convo_string).hexdigest()

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