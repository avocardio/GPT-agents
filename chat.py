import json
import datetime
import os
import sys

from utils.utils import get_response, truncate_context, summarize_chat_history, clear_terminal, preprompt, contains_search_keywords, slow_print
from utils.browsing import search
from utils.whisper import transcribe

# Pick one of the agents in agents/ with number keys
print("\n" + "\033[33m" + "agents:" + "\033[0m" + "\n")
agents = [f for f in os.listdir("agents") if os.path.isdir(os.path.join("agents", f))]
for index, agent in enumerate(agents, start=1):
    print(f"{index}. {agent}")

# Get the user input (number) and match it to the agent
op_index = input("\n" + "Choose a number or create a new one by running" + "\033[34m" + " agent_creator.py" + "\033[0m" + "\n"); clear_terminal()
agent = agents[int(op_index) - 1]

print(f"\nYou are now talking to {agent}.\n")

# Check for prior chat history
histories = summarize_chat_history(agent)

if histories is not None:
    history_index = input("\n" + "Choose where you left off or press" + "\033[34m" + " ENTER" + "\033[0m" + "\n"); clear_terminal()
    if history_index == "":
        history_file_path = f"agents/{agent}/chat_history.json"
    else:
        history_file_path = f"agents/{agent}/{histories[int(history_index) - 1]}"
else:
    history_file_path = f"agents/{agent}/chat_history.json"

# Load the chat history from the file
try:
    with open(history_file_path, "r") as f:
        chat_history = json.load(f)
except FileNotFoundError:
    chat_history = []

# Truncate the chat history to the last 2500 words
chat_history = truncate_context(chat_history)

# Define the request payload
payload = {
    "model": "gpt-3.5-turbo",
    "messages": [],
    "temperature": 0.7
}

# Convert chat history to messages for the payload
for message in chat_history:
    payload["messages"].extend([
        {"role": "user", "content": message["user"]},
        {"role": "assistant", "content": message[f"{agent}"]}
    ])

payload["messages"].insert(0, {"role": "system", "content": preprompt(agent)}) 

# Define the ANSI escape codes for the colors
USER_COLOR = "\033[32m"  # green
AI_COLOR = "\033[35m"  # purple
RESET_COLOR = "\033[0m"  # reset

with open("config.json", "r") as config:
    config = json.load(config)

while True:
    
    # Get the user input
    print("\n" + USER_COLOR + "You: " + RESET_COLOR, end="", flush=True)

    if config["STT_(WHISPER)"] == "True":
        user_input = transcribe()
        sys.stdout.write("\033[F")
        print(user_input)
    else:  
        user_input = input()

    if user_input.__contains__("RESET"):
        # Rename the chat history file to include the date and time
        os.rename(history_file_path, f"agents/{agent}/chat_history_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json")
        chat_history = []
        payload["messages"] = [{"role": "system", "content": preprompt(agent)}]
        continue

    if contains_search_keywords(user_input):
        print("\n" + AI_COLOR + f"{agent}: " + RESET_COLOR, end="")
        slow_print("Searching..." + "\n")
        payload["messages"].append(search(user_input))
    else:
        # Add the user message to the payload
        payload["messages"].append({"role": "user", "content": user_input})

    with open("config.json", "r") as config:
        config = json.load(config)

    if config["DEBUG"] != "False":
        print(f"\nDEBUG: {payload['messages']}\n")

    response = get_response(payload["messages"])

    # Print the AI message
    print("\n" + AI_COLOR + f"{agent}: " + RESET_COLOR, end="")
    slow_print(response)

    # Add the user and AI messages to the chat history
    chat_history.append({"user": user_input, f"{agent}": response})
    
    # Save the chat history to the file
    with open(history_file_path, "w") as f:
        json.dump(chat_history, f)

    # Add the AI message to the payload messages for the next request
    payload["messages"].append({"role": "assistant", "content": response})