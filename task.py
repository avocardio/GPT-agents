import json
import os
import sys
import random
from typing import List, Callable, Optional
import threading
import time

from utils.utils import get_response, short_preprompt, contains_search_keywords, slow_print
from utils.browsing import search


def get_best_agent(context: List[dict], agents: List[str], current_agent: Optional[str] = None):
    candidates = [{"role": "user", "content": f"Which agent is the best choice to continue? Reply only with the Agents name: {', '.join(agents)}"}]
    candidates.extend(context)

    response = get_response(candidates, temperature=0.1)
    # From the response, find the word that starts with a capital letter
    selected_agent = None
    for word in response.split():
        if word[0].isupper():
            selected_agent = word
            break

    selected_agent = response.strip() if response is not None else None

    if selected_agent not in agents:
        selected_agent = random.choice(agents)

    return selected_agent

def get_user_feedback(timeout: float = 20.0) -> Optional[str]:
    feedback_container = []

    def get_input(container: list):
        user_input = input("\n\n\033[31m"+"Feedback from user (or leave empty):\033[0m ")
        container.append(user_input)

    input_thread = threading.Thread(target=get_input, args=(feedback_container,))
    input_thread.start()

    input_thread.join(timeout)

    if input_thread.is_alive():
        print("\nProceeding with agent interaction...\n")
        return None

    feedback = feedback_container[0] if feedback_container else None
    return feedback if feedback and feedback.strip() else None

def goal_reached(messages, goal: str) -> bool:
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages + [{"role": "user", "content": f"Has the goal '{goal}' been reached? Respond with 'yes' or 'no'"}],
        "temperature": 0.7
    }

    response = get_response(payload["messages"])

    return response.lower() in ["yes", "true", "y", "t"]

def agent_interaction(goal: str):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [],
        "temperature": 0.7
    }

    # Get all the agents from the agents/ directory
    agents = [f for f in os.listdir("agents") if os.path.isdir(os.path.join("agents", f))]

    agent_descriptions = "\n\n".join(short_preprompt(agent) for agent in agents)
    messages = [{"role": "system", "content": f"The user has set a goal for you to work together: {goal}\n\nAgents available:\n{agent_descriptions}\n\nDifferent agents can be picked out, and browsing abilities, etc. are available by calling keywords like 'look up' or 'google'."}]

    selected_agent = 'Assistant'

    print("Your input is important! You have a 20-second window to provide feedback or instructions before agents switch or perform an action.")

    while True:
        # Extract initial goal and agent types information
        initial_info = messages[:1]

        # Get the best agent for the current context
        previous_agent = selected_agent
        selected_agent = get_best_agent(messages, agents, selected_agent)

        if previous_agent != selected_agent:
            switch_message = f"Now is the turn of {selected_agent}. What would you do next? Remember you can search the web by calling keywords like 'look up' or 'google'."
            messages.append({"role": "system", "content": switch_message})

        # Add agent's context to the messages
        payload["messages"] = initial_info + (messages[1:] if len(messages) < 11 else messages[-5:])

        print(f"\n\033[31mSelected agent: {selected_agent}\033[0m")

        # Debug mode
        with open("config.json", "r") as config:
            config = json.load(config)

        if config["DEBUG"] is not "False":
            print(f"\nDEBUG: {payload['messages']}\n")

        # Get agent's response
        response = get_response(payload["messages"])

        # If the agent's response contains search keywords, call the search function
        if contains_search_keywords(response):
            print("\n" + "\033[35m" + f"{selected_agent}: " + "\033[0m", end="")
            slow_print("Searching..." + "\n")
            search_result = search(response, mode="multi_agent_interaction")
            messages.append({"role": "assistant", "content": search_result})
        else:
            messages.append({"role": "assistant", "content": response})

        # Show agent's response
        print("\033[35m"+f"\n{selected_agent}: " + "\033[0m" + f"{response}\n")

        # Check if the goal has been reached
        if goal_reached(messages, goal):
            print("\033[0;33m"+f"Goal '{goal}' has been reached.\n"+"\033[0m")
            break

        # If user feedback function is provided, call it
        feedback = get_user_feedback()
        if feedback is not None:
            important_feedback = f"\n\nIMPORTANT! USE THIS FEEDBACK FROM USER: {feedback}\n"
            messages.append({"role": "user", "content": important_feedback})

goal = input("\n"+"Please input a goal or task for the agents: ")
agent_interaction(goal)