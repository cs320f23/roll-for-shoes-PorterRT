from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import pickle
import os

import tiktoken

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
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        self.final_count = 0
        self.buffered_messages = []

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def message(self, message):
        combined_message = f"{self.prompt}\n{message}"  # Use the prompt before the message
        token_count = self.count_tokens(combined_message)
        
        #print(f"Token count for message: {token_count}")
        

        self.message_history.append(HumanMessage(content=combined_message))
        resp = self.chat(self.message_history)

        response_token_count = self.count_tokens(resp.content)
        #print(f"Token count for response: {response_token_count}")
        print("\n")

        self.final_count += token_count + response_token_count
        #print(f"Token count total: {self.final_count}")

        self.buffered_messages = [HumanMessage(content=combined_message), resp]

        # If the buffer grows beyond a certain size (for instance, 4 entries), remove the oldest messages.
        while len(self.buffered_messages) > 4:  # Adjust to 4 for 2 messages and 2 responses
            self.buffered_messages.pop(0)

        if self.final_count > 4000:
            #print("Token limit reached. Buffering last interaction and starting a new conversation.")
            
            

            # Reset message history and token count.
            self.message_history = []
            self.final_count = 0

            # Add buffered messages back to the message history.
            self.message_history.extend(self.buffered_messages)
            for msg in self.buffered_messages:
                self.final_count += self.count_tokens(msg.content)

            # Clear the buffer.
            self.buffered_messages = []
            # You might want to send a placeholder message or prompt to guide the next interaction.
            return AIMessage(content="the game goes on")  

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

def game_over(message: str) -> bool:
    """Check if the game should end based on a message content."""
    end_phrases = ["you have died", "you have achieved your goal", "you win", "Game over!", "GAME OVER!",'"Game over!"'] 
    
    # Check each phrase
    for phrase in end_phrases:
        if phrase in message.lower():
            print(f"Game-over phrase '{phrase}' found in the message.")
            return True
            
    #print("No game-over phrase found in the message.")
    return False


message = "What is your character's name and what do they look like?"
current_agent = player
L = True
while(L == True):
    print(f"{current_agent.name}:")
    resp = current_agent.message(message)
    # Check if game over conditions are met
    print(f"Checking GM's message for game-over phrases: {resp.content}")
    if game_over(resp.content):
        print("Game Over!")
        L = False
        break
    message = resp.content
    if current_agent == player:
        current_agent = gm
    else:
        current_agent = player

print("out of loop")
        