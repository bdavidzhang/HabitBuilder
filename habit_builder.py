from openai import OpenAI
from dotenv import load_dotenv
import os
import json 

load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

if not deepseek_api_key:
    raise ValueError("DEEPSEEK_API_KEY not found in .env file or environment variables.")

client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

def goal_decomposition(goal: str) -> dict:
    """
    Takes a high-level goal and breaks it down into atomic habits using an AI model.
    """
    
    user_prompt = f"My main goal is: '{goal}'. Please break this down for me into concrete, actionable atomic habits. Follow the instructions and formatting guidelines you have been provided."

    system_prompt = """You are an expert AI habit formation coach inspired by James Clear's "Atomic Habits". Your primary role is to help users break down large goals into small, manageable, and identity-based habits.

You must respond with only a valid JSON object, without any introductory text, explanations, or markdown formatting.

The JSON object must follow this exact structure:
{
  "identity_shift": "A concise statement describing the new identity the user is building. Start with 'You are becoming someone who...'",
  "atomic_habits": [
    {
      "habit_name": "A specific, small, and actionable habit that contributes to the main goal.",
      "two_minute_version": "The easiest possible version of this habit that can be completed in under two minutes. This is the starting point.",
      "rationale": "A brief explanation of how this small habit helps achieve the larger goal and reinforces the new identity."
    }
  ]
}

Please generate 2 to 4 relevant `atomic_habits` for the user's goal.
"""

    response = client.chat.completions.create(
        model="deepseek-chat", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1500,
        response_format={"type": "json_object"} # Use this if the API supports it for guaranteed JSON output
    )
    
    # The response content will be a JSON string, so it should be parsed.
    try:
        decomposed_goals = json.loads(response.choices[0].message.content)
        return decomposed_goals
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the model's response.")
        print("Raw response:", response.choices[0].message.content)
        return {}

if __name__ == '__main__':
    # You can change the user_goal to test different scenarios
    user_goal = input("Enter your goal here:")
    
    print(f"Breaking down the goal: '{user_goal}'\n")
    
    decomposed_habits = goal_decomposition(user_goal)
    
    # Pretty-print the dictionary to see the structured output
    if decomposed_habits:
        print(json.dumps(decomposed_habits, indent=2))