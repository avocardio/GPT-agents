# GPT-agents 

GPT-agents is a simple blend between AutoGPT and Perplexity AI, with a focus on usability and user experience.

| 💼 `Assistant` | 💭 `Therapist` | 👨‍🍳 `Chef` | 👔 `Investor` |
|----------|----------|----------|----------|
| The default agent, with a neutral personality         |   A therapist that can help you with your problems       |    A chef with great cooking expertise      |   An agent that has knowledge about finance and investments       |


Features: 

- 🌐 Browsing capabilities: The agents can browse and search for information to assist you better
- 📝 Conversation history: Save and load conversation history
- ✏️ Agent management: Easily create and manage multiple agents
- 🗣️ Conversation: Use the Whisper API to transcribe speech-to-text for a more seamless 1-1 communication experience

There are two options: __chat__ mode and __task__ mode. In chat mode, you can converse with the agent, and in task mode, you can let all agents work together to complete a task.

____________________________________________________

## Setup

1. Clone the repository:
```
git clone https://github.com/avocardio/GPT-agents.git
```
2. Install the requirements:
```
pip install -r requirements.txt
```
3. Store your OpenAI API key in and change the name of the file to:

`credentials.json` (without the "(template)")

4. Edit the `config.json` file to your liking

5. Run the program:
```
python chat.py
```
or 
```
python task.py
```

## Usage

__Chat mode__

- Follow the on-screen instructions to select an agent (1-4), and then select the conversation history to be used, or press enter to use the current history. After this, you will be able to converse with the agent.

- To reset and save a conversation, type **"RESET"** into the input field and press enter. This will save the current conversation to a timestamped `history.json` file in the agent's folder. After this, you will have a fresh instance of the agent.

__Task mode__

- In this mode, you will be prompted to enter a task. The agents will then talk to each other and pick new agents from the pool to complete the task. The agents will also be able to browse the internet for information to help them complete the task.

## Features

__Agents__

- Currently there are 4 agents available.

    To create more agents, simply create a file in the `agents` folder, and add a JSON file, or run the `agent_creator.py` script.

__Browsing__

- Browsing is enabled when the user prompts using one of the following keywords:

    `["search", "browse", "research", "look up", "find", "look for", "google", "browsing", "googling", "looking for", "looking up", "looking up"]`

    This will trigger a google search where the first 3 pages are scraped and summarized, for the agent to read out to the user.

__Whisper API__

- To use voice to text with the agents, you will need to enable this function in `config.json`. Then, you will be able to speak to the agent when its your turn ("You:") and accept the message with enter.

## Examples

a) Chef

![Chef Example](https://drive.google.com/uc?id=1yvdbwZMC45X88_FTROM9IK7u1tIHRuEt)

b) Investor

![Investor Example](https://drive.google.com/uc?id=1DJVfbDpz6QsOpxV3f4c-9Uj4iqSIrNkT)

## Debug mode

To print the current message payload sent to the model (for debugging) you can enable debug-mode in the config.json file.

## Todo's

- Fix Voice input newline when accepting with enter
- Add more agents
- Improve task setting
- Improve browsing capabilities
- Add TTS (coqui-ai TTS)
- Add telegram / discord support
