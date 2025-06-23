#!/usr/bin/env python3
"""
Test script to verify all Flask endpoints work properly
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_goal_decomposition():
    """Test the goal decomposition endpoint"""
    print("Testing Goal Decomposition...")
    response = requests.post(f"{BASE_URL}/decompose_goal", 
                            json={"goal": "Learn to play guitar"})
    if response.status_code == 200:
        print("✅ Goal decomposition works!")
        print(json.dumps(response.json(), indent=2)[:200] + "...")
    else:
        print(f"❌ Goal decomposition failed: {response.status_code}")

def test_habit_stacking():
    """Test the habit stacking endpoint"""
    print("\nTesting Habit Stacking...")
    response = requests.post(f"{BASE_URL}/stack_habits", 
                            json={
                                "current_habits": ["Make coffee", "Brush teeth"],
                                "desired_habits": ["Read for 5 minutes", "Do push-ups"]
                            })
    if response.status_code == 200:
        print("✅ Habit stacking works!")
        print(json.dumps(response.json(), indent=2)[:200] + "...")
    else:
        print(f"❌ Habit stacking failed: {response.status_code}")

def test_reduce_friction():
    """Test the reduce friction endpoint"""
    print("\nTesting Reduce Friction...")
    response = requests.post(f"{BASE_URL}/reduce_friction", 
                            json={"habit": "Exercise for 1 hour daily"})
    if response.status_code == 200:
        print("✅ Reduce friction works!")
        print(json.dumps(response.json(), indent=2)[:200] + "...")
    else:
        print(f"❌ Reduce friction failed: {response.status_code}")

def test_habit_tracking():
    """Test the habit tracking endpoint"""
    print("\nTesting Habit Tracking...")
    response = requests.post(f"{BASE_URL}/track_habit", 
                            json={
                                "habit_name": "Morning Exercise",
                                "completed": True,
                                "date": "2025-06-23"
                            })
    if response.status_code == 200:
        print("✅ Habit tracking works!")
        print(response.json())
    else:
        print(f"❌ Habit tracking failed: {response.status_code}")

def test_static_serving():
    """Test that the React app is served properly"""
    print("\nTesting Static File Serving...")
    response = requests.get(BASE_URL)
    if response.status_code == 200 and "HabitBuilder" in response.text:
        print("✅ React app is served properly!")
    else:
        print(f"❌ Static serving failed: {response.status_code}")

if __name__ == "__main__":
    print("🧪 Testing HabitBuilder Flask App Endpoints")
    print("=" * 50)
    
    try:
        test_static_serving()
        test_goal_decomposition()
        test_habit_stacking()
        test_reduce_friction()
        test_habit_tracking()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed! Check the results above.")
        print("\n📱 Open http://localhost:5001 in your browser to use the app!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the Flask app. Make sure it's running on port 5001.")
        print("   Run: python app.py")
