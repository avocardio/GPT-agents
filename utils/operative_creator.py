import os
import json

# Get the agent's attributes from the user
agent_name = input("\n" + "Enter agent's name: ")
agent_description = input("Enter agent's description: ")
agent_personality = input("Enter agent's personality: ")
agent_example = input("Enter agent's example message: ")

# Create the operative dictionary
agent = {
    "name": agent_name,
    "description": agent_description,
    "personality": agent_personality,
    "example": agent_example
}

os.makedirs(f"agents/{agent_name}", exist_ok=True)

# Save the agent to a JSON file
agent_file_path = os.path.join(f'agents/{agent_name}', f"{agent_name}.json")
with open(agent_file_path, "w") as f:
    json.dump(agent, f, indent=2)

print(f"\n{agent['name']} saved to agents.")