import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# --- Configuration and API Client Setup ---
load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

if not deepseek_api_key:
    raise ValueError("DEEPSEEK_API_KEY not found in .env file or environment variables.")

# Initialize the client to connect to the DeepSeek API
client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

# --- File Handling Functions ---

def create_sample_habits_file(filepath: str = "habits.json"):
    """Creates a sample JSON file with current and desired habits."""
    if os.path.exists(filepath):
        return # Don't overwrite an existing file
        
    sample_data = {
        "current_habits": [
            "Make my morning coffee",
            "Finish dinner",
            "Get into bed",
            "Arrive at my office desk",
            "Brush my teeth"
        ],
        "desired_habits": [
            "Read one page of a book",
            "Floss my teeth",
            "Meditate for 1 minute",
            "Review my to-do list for the day",
            "Tidy up the kitchen"
        ]
    }
    with open(filepath, 'w') as f:
        json.dump(sample_data, f, indent=2)
    print(f"Sample '{filepath}' created.")

def read_habits_from_file(filepath: str = "habits.json") -> dict:
    """Reads the habits from the specified JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: The file '{filepath}' is not a valid JSON file.")
        return {}

# --- Core AI Habit Stacking Function ---

def generate_habit_stacks(current_habits: list, desired_habits: list) -> dict:
    """
    Uses an LLM to stack desired habits onto current habits to maximize motivation.
    
    Args:
        current_habits: A list of habits the user already performs regularly.
        desired_habits: A list of new habits the user wants to build.
        
    Returns:
        A dictionary containing the logically stacked habits.
    """
    
    # The system prompt sets the persona, context, and rules for the AI.
    system_prompt = """
You are an expert AI habit formation coach specializing in the "Habit Stacking" technique from James Clear's "Atomic Habits." Your task is to create logical and motivating habit stacks by pairing new, desired habits with existing, current habits.

The key to maximizing motivation is to link habits that are similar in context, time, and location. For example, stack a morning habit with another morning habit. Stack a habit you do in the kitchen with another kitchen-based one.

You must respond with only a valid JSON object. Do not include any text or markdown before or after the JSON. The JSON object must have a single key "habit_stacks" which contains a list of stack objects.

Each stack object in the list must follow this exact structure:
{
  "anchor_habit": "The existing habit from the current habits list.",
  "new_habit": "The new habit from the desired habits list that is being stacked.",
  "stack_formula": "The complete stack phrase, following the 'After [CURRENT HABIT], I will [NEW HABIT]' formula.",
  "reasoning": "A brief, one-sentence explanation for why this is a motivating and logical pairing based on context, location, or timing."
}

Pair as many of the desired habits as you can with a suitable anchor habit.
"""

    # The user prompt clearly presents the data for the AI to process.
    user_prompt = f"""
Here are my habits. Please create the habit stacks.

Current Habits (my anchors):
{json.dumps(current_habits, indent=2)}

Desired Habits (the new ones I want to build):
{json.dumps(desired_habits, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            # Using a coder model is often best for strict JSON compliance
            model="deepseek-coder", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000,
            # This ensures the model output is a clean JSON object
            response_format={"type": "json_object"} 
        )
        
        # The response content will be a JSON string, so it should be parsed.
        stacked_habits = json.loads(response.choices[0].message.content)
        return stacked_habits

    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from the model's response. {e}")
        print("Raw response:", response.choices[0].message.content)
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}

# --- Main Execution Block ---

if __name__ == '__main__':
    habits_file = "habits.json"
    
    # 1. Create a sample habits file if it doesn't exist
    create_sample_habits_file(habits_file)
    
    # 2. Read the habits from the file
    habits_data = read_habits_from_file(habits_file)
    
    if habits_data:
        current = habits_data.get("current_habits", [])
        desired = habits_data.get("desired_habits", [])
        
        print("--- Input Habits ---")
        print("Current:", current)
        print("Desired:", desired)
        print("\nSending to AI for habit stacking...\n")
        
        # 3. Call the AI to generate the stacks
        stacked_result = generate_habit_stacks(current, desired)
        
        # 4. Pretty-print the final JSON output
        if stacked_result:
            print("--- AI Generated Habit Stacks ---")
            print(json.dumps(stacked_result, indent=2))
