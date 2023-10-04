from dotenv import load_dotenv
import pickle
import os
load_dotenv()

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

class Agent:
    def __init__(self, name, prompt, history_file=None):
        # Initialize the class
        self.name = name
        self.prompt = prompt
        self.chat = ChatOpenAI(streaming=True, 
                               callbacks=[StreamingStdOutCallbackHandler()], 
                               temperature=1.0,
                               model="gpt-4",)
        self.message_history = [] 

    def message(self, message):
        combined_message = f"{self.prompt}\n{message}"
        self.message_history.append(HumanMessage(content=combined_message))
        resp = self.chat(self.message_history)
        print("\n")
        self.message_history.append(resp)
        self.save_conversation(f"{self.name}_conversation.json")
        return resp

    def save_conversation(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.message_history, f)

all_header = "" # replace this with appropriate value or fetch it

with open("gm_header.txt") as f:
    gm_header = all_header + f.read()

gm = Agent("GM", gm_header)

with open("player_header.txt") as f:
    player_header = all_header + f.read()
player = Agent("Player", player_header)

message = "what is your character name and what do they look like?"
# ^ tried to make this as token manipulative as possible.
current_agent = player
while True:
    print(f"{current_agent.name}:")
    resp = current_agent.message(message)
    message = resp.content
    if current_agent == player:
        current_agent = gm
    else:
        current_agent = player
