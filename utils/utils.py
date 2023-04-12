import requests
import json
import os
import json
import subprocess
import sys
import time

with open("credentials.json", "r") as file:
    credentials = json.load(file)

OPENAI_API_KEY = credentials.get("OPENAI_API_KEY")

def clear_terminal():
    command = "cls" if os.name == "nt" else "clear"
    subprocess.run(command, shell=True)

def slow_print(text):

    with open("config.json", "r") as config:
        config = json.load(config)

    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(config.get("CHAT_DELAY"))
    print()

def get_response(messages, temperature=0.7, max_tokens=None):

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": temperature
    }
    
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response_data = json.loads(response.text)

    try: 
        return response_data["choices"][0]["message"]["content"]
    except KeyError:
        print(response_data["error"])

def word_count(text):
    return len(text.split())

def truncate_context(chat_history, max_words=2000):
    total_words = 0
    truncated_history = []

    for message_pair in reversed(chat_history):
        user_key = [key for key in message_pair if key == 'user'][0]
        assistant_key = [key for key in message_pair if key != 'user'][0]

        user_words = word_count(message_pair[user_key])
        assistant_words = word_count(message_pair[assistant_key])
        pair_words = user_words + assistant_words

        if total_words + pair_words <= max_words:
            truncated_history.insert(0, message_pair)
            total_words += pair_words
        else:
            break

    return truncated_history

def summarize_chat_history(agent_name):
    agent_dir = os.path.join("agents", agent_name)

    # Load and summarize chat history files
    chat_history_files = sorted([f for f in os.listdir(agent_dir) if f.startswith("chat_history")])

    if len(chat_history_files) == 0:
        return

    print("\033[34m" + f"\nHistory of {agent_name}:" + "\033[0m" + "\n")

    for index, chat_history_file in enumerate(chat_history_files, start=1):
        with open(os.path.join(agent_dir, chat_history_file), "r") as f:
            chat_history = json.load(f)

        # Convert chat history to messages for the payload
        messages = []
        for message in chat_history:
            messages.extend([
                {"role": "user", "content": message["user"]},
                {"role": "assistant", "content": message[f"{agent_name}"]}
            ])

        summary = get_response(messages + [{"role": "user", "content": "Briefly summarize the main topic of this conversation in 10 words or less. Topic (dont use \"\"):"}], max_tokens=20).strip()

        if index == 1:
            print(f"{index} - (Current) {summary}")
        else:
            print(f"{index} - {summary}")

    # Return index and names of chat history files
    return chat_history_files

def preprompt(agent_name):

    with open(os.path.join("agents", agent_name, f"{agent_name}.json"), "r") as f:
        op_config = json.load(f)

    name = op_config["name"]
    description = op_config["description"]
    personality = op_config["personality"]
    example = op_config["example"]

    preprompt = f"You are a helpful {name} AI, your name is \"{name}\". You are: {personality}. {description}. Here is an example of how you might respond to a user: '{example}'"

    return preprompt

def contains_search_keywords(user_input):
    keywords = ["search", "browse", "research", "look up", "find", "look for", "google", "browsing", "googling", "looking for", "looking up", "looking up"]
    for keyword in keywords:
        if user_input.lower().__contains__(keyword):
            return True
    return False
