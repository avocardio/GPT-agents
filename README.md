# GPT-agents 

GPT-agents is a simple blend between AutoGPT and Perplexity AI, with a focus on usability and user experience. 

Features: 

- 🌐 Browsing capabilities: The AI can browse and search for information to assist you better
- 🫂 Multiple agents: Choose from a variety of agents with different personalities and roles
- ✏️ Agent management: Easily create and manage multiple agents
- 🗣️ Conversation option: Use the Whisper API to transcribe speech-to-text for a more seamless 1-1 communication experience

## Features

### Agents

Currently there are 4 agents available:

- 💼 `Assistant`: The default agent, with a neutral personality
- 💭 `Therapist`: A therapist that can help you with your problems
- 👨‍🍳 `Chef`: A chef with great cooking expertise
- 👔 `Investor`: An agent that has knowledge about finance and investments

To create more agents, simply create a file in the `agents` folder, and add a JSON file, or run the `agent_creator.py` script.

### Browsing

Browsing is enabled when the user prompts using one of the following keywords:

`["search", "browse", "research", "look up", "find", "look for", "google", "browsing", "googling", "looking for", "looking up", "looking up"]`

This will trigger a google search where the first (max) 3 pages are scraped and summarized, for the agent to read out to the user.

### Whisper API

To use voice to text with the agents, you will need to enable this function in `config.json`. Then, you will be able to speak to the agent when its your turn ("You:") and accept the message with enter.

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
python main.py
```

## Usage

Follow the on-screen instructions to select an agent (1-4), and then select the conversation history to be used, or press enter to use the current history. After this, you will be able to converse with the agent.

To reset and save a conversation, type **"RESET"** into the input field and press enter. This will save the current conversation to a timestamped `history.json` file in the agent's folder. After this, you will have a fresh instance of the agent.

## Examples

a) Chef

![Chef Example](https://drive.google.com/uc?id=1yvdbwZMC45X88_FTROM9IK7u1tIHRuEt)

b) Investor

![Investor Example](https://drive.google.com/uc?id=1DJVfbDpz6QsOpxV3f4c-9Uj4iqSIrNkT)

## Todo's

- Add more agents
- Add inter-agent communication and creation (recursion)
- Add TTS (coqui-ai TTS)
- Improve browsing capabilities
- Add telegram / discord support