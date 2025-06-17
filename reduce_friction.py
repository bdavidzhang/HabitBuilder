import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta
import uuid

# --- Configuration and API Client Setup ---
load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

if not deepseek_api_key:
    raise ValueError("DEEPSEEK_API_KEY not found in .env file or environment variables.")

# Initialize the client to connect to the DeepSeek API
client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

# --- Feature 1: Habit Deconstruction & Gradual Progression ---

def deconstruct_complex_habit(complex_habit: str) -> dict:
    """
    Breaks down a complex habit into a simple, step-by-step progression plan.
    """
    system_prompt = """
You are an expert AI habit formation coach. Your task is to deconstruct a user's complex goal into a simple, 4-week progression plan. Each week should build on the last, starting with an extremely easy "two-minute" version.

You must respond with only a valid JSON object. The root object should contain a key "progression_plan" which is a list of four week objects.

Each week object must have this exact structure:
{
  "week": <week_number>,
  "focus": "The theme or goal for the week.",
  "action": "The specific, concrete action the user should take this week."
}
"""
    user_prompt = f"Please deconstruct this complex goal into a 4-week plan: '{complex_habit}'"

    try:
        response = client.chat.completions.create(
            model="deepseek-coder",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"An error occurred in deconstruct_complex_habit: {e}")
        return {}

# --- Feature 2: Proactive Problem-Solving for Missed Habits ---

def analyze_and_adjust_habit(habit: str, history: list[bool]) -> dict:
    """
    Analyzes a user's habit history and suggests adjustments for missed habits.
    """
    system_prompt = """
You are an empathetic and supportive AI habit coach. You have noticed the user is struggling with a habit. Your task is to offer gentle, non-judgmental suggestions for making the habit easier, based on the principles of "Atomic Habits".

You must respond with only a valid JSON object with two keys: "observation" and "suggestions".
- "observation": A kind, non-judgmental sentence acknowledging the user's effort and the difficulty.
- "suggestions": A list of 2-3 concrete, actionable ideas to make the habit easier (e.g., reduce the time, change the environment, or simplify the action).
"""
    user_prompt = f"""
I'm trying to build the habit: '{habit}'.
Here is my completion history for the last 7 days (True=completed, False=missed): {history}.
Please give me some suggestions.
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat", # A chat model is better for empathetic responses
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"An error occurred in analyze_and_adjust_habit: {e}")
        return {}

# --- Feature 3: Integration with Other Apps (Calendar Example) ---

def create_calendar_integration(habit: str, start_time: datetime):
    """
    Creates an iCalendar (.ics) file to integrate a habit into a calendar app.
    """
    end_time = start_time + timedelta(minutes=30) # Default to a 30-minute block
    
    # Standard iCalendar format
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//HabitFormingAI//EN
BEGIN:VEVENT
UID:{uuid.uuid4()}
DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start_time.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_time.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{habit}
DESCRIPTION:This event was created by your AI Habit Coach to help you stay on track!
END:VEVENT
END:VCALENDAR
"""
    filename = f"{habit.replace(' ', '_').lower()}.ics"
    with open(filename, 'w') as f:
        f.write(ics_content)
    
    print(f"✅ Integration successful! Calendar event file created: '{filename}'")
    print("   You can import this file into Google Calendar, Apple Calendar, or Outlook.")


# --- Main Execution Block ---

if __name__ == '__main__':
    print("--- 1. Habit Deconstruction & Gradual Progression ---")
    complex_habit_goal = "Learn to cook healthy meals"
    print(f"Deconstructing complex habit: '{complex_habit_goal}'\n")
    plan = deconstruct_complex_habit(complex_habit_goal)
    if plan:
        print(json.dumps(plan, indent=2))
    
    print("\n" + "="*50 + "\n")

    print("--- 2. Proactive Problem-Solving for Missed Habits ---")
    struggling_habit = "Go for a 30-minute run every morning"
    # Simulate a user struggling mid-week
    habit_history = [True, True, False, True, False, False, False] 
    print(f"Analyzing struggles with habit: '{struggling_habit}'")
    print(f"History: {habit_history}\n")
    adjustment = analyze_and_adjust_habit(struggling_habit, habit_history)
    if adjustment:
        print(json.dumps(adjustment, indent=2))

    print("\n" + "="*50 + "\n")

    print("--- 3. Integration with Other Apps (Calendar) ---")
    habit_to_schedule = "Evening Walk"
    # Schedule for tomorrow at 6:00 PM
    event_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=1)
    print(f"Creating a calendar event for '{habit_to_schedule}' at {event_time.strftime('%Y-%m-%d %I:%M %p')}\n")
    create_calendar_integration(habit_to_schedule, event_time)
