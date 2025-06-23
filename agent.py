import os
import json
import uuid
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta

# --- Firebase Admin SDK for Database ---
# You'll need to install this library: pip install firebase-admin
import firebase_admin
from firebase_admin import credentials, firestore

# --- Configuration and API Client Setup ---
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

if not api_key:
    raise ValueError("API key not found. Please set DEEPSEEK_API_KEY or OPENAI_API_KEY in your .env file.")

# --- Firebase Initialization ---
def initialize_firestore():
    """Initializes the Firebase Admin SDK to connect to Firestore."""
    try:
        # Check if the app is already initialized to prevent errors.
        if not firebase_admin._apps:
            # IMPORTANT: Create a 'firebase_credentials.json' file from your Firebase project settings.
            # Go to Project Settings > Service accounts > Generate new private key
            cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except FileNotFoundError:
        print("="*60)
        print("ERROR: 'firebase_credentials.json' not found.")
        print("Please download your service account key from the Firebase console")
        print("and place it in the same directory as this script.")
        print("="*60)
        return None
    except Exception as e:
        print(f"An unexpected error occurred during Firebase initialization: {e}")
        return None

class HabitAgent:
    """
    A comprehensive AI agent for habit formation, using Firestore as its memory.
    """
    def __init__(self, user_id: str, db_client, model: str = "deepseek-chat"):
        """
        Initializes the agent with a user ID and database/AI clients.
        """
        self.user_id = user_id
        self.model = model
        self.db = db_client
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        # The user's entire state is represented by a single document in Firestore.
        self.user_ref = self.db.collection('users').document(self.user_id)
        self.memory = self._load_memory()

    # --- Core Memory and State Management (Now with Firestore) ---

    def _load_memory(self) -> dict:
        """Loads the agent's memory for the user from a Firestore document."""
        try:
            doc = self.user_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                # First-time user setup: create the initial structure.
                default_memory = {
                    "user_id": self.user_id,
                    "main_goal": None,
                    "identity_shift": None,
                    "habits": {},
                    "conversation_log": []
                }
                # Save this initial structure to the database immediately.
                self.user_ref.set(default_memory)
                return default_memory
        except Exception as e:
            print(f"Error loading memory from Firestore: {e}")
            # Fallback to a temporary local memory if Firestore fails.
            return {}


    def _save_memory(self):
        """Saves the agent's current memory state to its Firestore document."""
        try:
            self.user_ref.set(self.memory)
        except Exception as e:
            print(f"Error saving memory to Firestore: {e}")


    def _log_interaction(self, role: str, content: str):
        """Logs a message to the conversation history in memory."""
        # Use Firestore's server timestamp for accuracy.
        log_entry = {
            "role": role,
            "content": content,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        # Use array_union to append to the log in an atomic way.
        self.user_ref.update({
            'conversation_log': firestore.ArrayUnion([log_entry])
        })
        # Also update local memory to stay in sync.
        # Note: In a real app, you might re-fetch after updating.
        self.memory.get("conversation_log", []).append(log_entry)


    # --- Agent "Skills" / Tools (Logic remains the same, relies on _save_memory) ---

    def deconstruct_complex_habit(self, complex_habit: str) -> dict:
        """Skill: Breaks a complex goal into a 4-week progression plan."""
        self.memory["main_goal"] = complex_habit
        self._log_interaction("user", f"Wants to deconstruct goal: {complex_habit}")

        system_prompt = """
You are an expert AI habit formation coach. Your task is to deconstruct a user's complex goal into a simple, 4-week progression plan. You must respond with only a valid JSON object with two keys: "identity_shift" and "progression_plan".
"identity_shift": A concise statement like 'You are becoming someone who...'.
"progression_plan": A list of four week objects, each with "week", "focus", and "action".
"""
        user_prompt = f"Please deconstruct this complex goal into a 4-week plan: '{complex_habit}'"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.7, response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            self.memory['identity_shift'] = data.get('identity_shift')
            for week_plan in data.get("progression_plan", []):
                habit_name = week_plan['action']
                if habit_name not in self.memory['habits']:
                    self.memory['habits'][habit_name] = {"history": [], "stacked_on": None}
            self._save_memory()
            return data
        except Exception as e:
            print(f"An error occurred in deconstruct_complex_habit: {e}")
            return {}

    def analyze_and_adjust_habit(self, habit: str) -> dict:
        """Skill: Analyzes a struggling habit and suggests adjustments."""
        history = self.memory["habits"].get(habit, {}).get("history", [])
        if not history: return {}
        self._log_interaction("agent", f"Analyzing struggling habit: {habit}")

        system_prompt = """
You are an empathetic AI habit coach. You have noticed the user is struggling. Offer gentle suggestions based on "Atomic Habits". Respond with a JSON object with "observation" and "suggestions".
"""
        user_prompt = f"I'm trying to build the habit: '{habit}'. Here is my completion history for the last 7 days (True=completed, False=missed): {history[-7:]}. Please give me some suggestions."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.8, response_format={"type": "json_object"}
            )
            adjustment = json.loads(response.choices[0].message.content)
            self._log_interaction("agent", f"Suggested adjustment for {habit}: {adjustment['suggestions']}")
            return adjustment # No need to save here, as no memory was changed.
        except Exception as e:
            print(f"An error occurred in analyze_and_adjust_habit: {e}")
            return {}

    def create_calendar_integration(self, habit: str, start_time: datetime):
        """Skill: Creates an iCalendar (.ics) file."""
        end_time = start_time + timedelta(minutes=30)
        ics_content = f"""BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//HabitFormingAI//EN\nBEGIN:VEVENT\nUID:{uuid.uuid4()}\nDTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}\nDTSTART:{start_time.strftime('%Y%m%dT%H%M%S')}\nDTEND:{end_time.strftime('%Y%m%dT%H%M%S')}\nSUMMARY:{habit}\nDESCRIPTION:Event created by your AI Habit Coach.\nEND:VEVENT\nEND:VCALENDAR"""
        filename = f"{self.user_id}_{habit.replace(' ', '_').lower()}.ics"
        with open(filename, 'w') as f:
            f.write(ics_content)
        print(f"✅ Integration successful! Calendar event file created: '{filename}'")
        self._log_interaction("agent", f"Created calendar event for '{habit}'.")

    # --- Agent's Reasoning Loop ---

    def run_daily_check(self):
        """Simulates the agent's proactive daily check."""
        print(f"\n--- AGENT: Running daily check for user {self.user_id} on {datetime.now().date()} ---")
        self._log_interaction("agent", "Running daily check.")
        
        struggling_habits = []
        for habit, details in self.memory["habits"].items():
            recent_history = details.get("history", [])[-7:]
            missed_days = recent_history.count(False)
            if missed_days >= 3:
                struggling_habits.append(habit)
        
        if not struggling_habits:
            print("AGENT: User is on track. Great work!")
            self._log_interaction("agent", "User is on track. No intervention needed.")
            return

        print(f"AGENT: Detected user is struggling with: {', '.join(struggling_habits)}")
        for habit in struggling_habits:
            print(f"\n--- AGENT: Offering proactive support for '{habit}' ---")
            adjustment = self.analyze_and_adjust_habit(habit)
            if adjustment:
                print(f"MESSAGE TO USER: {adjustment['observation']}")
                for i, suggestion in enumerate(adjustment['suggestions']):
                    print(f"Suggestion {i+1}: {suggestion}")
        self._save_memory()

    def log_habit_completion(self, habit: str, did_complete: bool):
        """Logs the completion status of a habit."""
        if habit in self.memory.get('habits', {}):
            # This is a key change for Firestore: update the specific field.
            self.user_ref.update({
                f'habits.{habit}.history': firestore.ArrayUnion([did_complete])
            })
            # Also update local memory to stay in sync for the rest of the session.
            self.memory['habits'][habit]['history'].append(did_complete)
            status = "Completed" if did_complete else "Missed"
            print(f"USER: Logged '{habit}' as '{status}' for {datetime.now().date()}.")
            self._log_interaction("user", f"Logged habit '{habit}' as {did_complete}")
        else:
            print(f"AGENT: Error - Habit '{habit}' not found in memory.")

# --- Main Execution Block: Simulating a User's Journey ---

if __name__ == '__main__':
    db = initialize_firestore()
    
    if db:
        user_id = "user_firestore_123"
        agent = HabitAgent(user_id, db)

        if not agent.memory.get("main_goal"):
            print("--- DAY 1: User Onboarding with Firestore ---")
            goal = "Get fit and run a 5k"
            print(f"USER: My goal is to '{goal}'.")
            plan = agent.deconstruct_complex_habit(goal)
            if plan:
                print("\nAGENT: Here is your personalized progression plan:")
                print(json.dumps(plan, indent=2))
            
            first_habit = plan['progression_plan'][0]['action']
            event_time = datetime.now().replace(hour=7, minute=0, second=0) + timedelta(days=1)
            agent.create_calendar_integration(first_habit, event_time)
            print("-" * 50)

        # Simulate a week of progress
        habits_to_log = list(agent.memory['habits'].keys())
        # To prevent re-logging on every run, we'll check the history length
        if len(agent.memory['habits'][habits_to_log[0]]['history']) < 2:
            agent.log_habit_completion(habits_to_log[0], True)
            agent.log_habit_completion(habits_to_log[0], True)

        if len(habits_to_log) > 1 and len(agent.memory['habits'][habits_to_log[1]]['history']) < 5:
            agent.log_habit_completion(habits_to_log[1], True)
            agent.log_habit_completion(habits_to_log[1], False)
            agent.log_habit_completion(habits_to_log[1], True)
            agent.log_habit_completion(habits_to_log[1], False)
            agent.log_habit_completion(habits_to_log[1], False)

        # Proactive Agent Intervention
        agent.run_daily_check()
