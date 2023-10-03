from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import pickle
import os

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

class Agent:
    def __init__(self, name, prompt, history_file=None):
        self.name = name
        self.prompt = prompt
        self.message_history = []  # Initialize message_history
        self.chat = ChatOpenAI(streaming=True, 
                               callbacks=[StreamingStdOutCallbackHandler()], 
                               temperature=1.0,
                               model="gpt-4",)

    def message(self, message):
        combined_message = f"{self.prompt}\n{message}"  # Use the prompt before the message
        self.message_history.append(HumanMessage(content=combined_message))
        resp = self.chat(self.message_history)
        print("\n")
        self.message_history.append(resp)
        self.save_conversation(f"{self.name}_conversation.json")
        return resp

    def save_conversation(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.message_history, f)

# You might want to define or fetch the values for all_header, gm_header, and player_header.
all_header = ""  # Replace this with appropriate value or fetch it

with open("gm_header.txt") as f:
    gm_header = all_header + f.read()

gm = Agent("GM", gm_header)

with open("player_header.txt") as f:
    player_header = all_header + f.read()

player = Agent("Player", player_header)
message = "What is your character's name and what do they look like?"
current_agent = player
while True:
    print(f"{current_agent.name}:")
    resp = current_agent.message(message)
    message = resp.content
    if current_agent == player:
        current_agent = gm
    else:
        current_agent = player