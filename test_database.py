#!/usr/bin/env python3
"""
Test script to verify database operations work correctly
"""
import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_database_integration():
    """Test all database-powered endpoints"""
    print("🧪 Testing HabitBuilder Database Integration")
    print("=" * 60)
    
    # Test 1: Create/Get User
    print("\n1. Testing User Management...")
    user_response = requests.post(f"{BASE_URL}/api/users", 
                                json={"username": "test_user", "email": "test@example.com"})
    if user_response.status_code == 200:
        user_data = user_response.json()
        user_id = user_data['id']
        print(f"✅ User created/retrieved: {user_data['username']} (ID: {user_id})")
    else:
        print(f"❌ User creation failed: {user_response.status_code}")
        return
    
    # Test 2: Goal Decomposition with Database Storage
    print("\n2. Testing Goal Decomposition with Database Storage...")
    goal_response = requests.post(f"{BASE_URL}/decompose_goal", 
                                 json={"goal": "Learn to cook healthy meals", "user_id": user_id})
    if goal_response.status_code == 200:
        goal_data = goal_response.json()
        print(f"✅ Goal decomposed and stored in database!")
        print(f"   Identity shift: {goal_data.get('identity_shift', '')[:50]}...")
        created_habits = goal_data.get('created_habits', [])
        print(f"   Created {len(created_habits)} habits in database")
        if created_habits:
            habit_id = created_habits[0]['id']
            habit_name = created_habits[0]['name']
            print(f"   First habit: {habit_name} (ID: {habit_id})")
    else:
        print(f"❌ Goal decomposition failed: {goal_response.status_code}")
        return
    
    # Test 3: Habit Tracking
    print("\n3. Testing Habit Tracking...")
    track_response = requests.post(f"{BASE_URL}/track_habit", 
                                  json={
                                      "user_id": user_id,
                                      "habit_id": habit_id,
                                      "completed": True,
                                      "date": "2025-06-27",
                                      "notes": "Felt great today!",
                                      "difficulty_rating": 3
                                  })
    if track_response.status_code == 200:
        track_data = track_response.json()
        print(f"✅ Habit tracked successfully!")
        print(f"   Message: {track_data['message']}")
    else:
        print(f"❌ Habit tracking failed: {track_response.status_code}")
    
    # Test 4: Get User Habits
    print("\n4. Testing Get User Habits...")
    habits_response = requests.get(f"{BASE_URL}/api/users/{user_id}/habits")
    if habits_response.status_code == 200:
        habits_data = habits_response.json()
        print(f"✅ Retrieved {len(habits_data)} habits for user")
        for habit in habits_data[:2]:  # Show first 2 habits
            print(f"   - {habit['name']} (Created: {habit['created_at'][:10]})")
    else:
        print(f"❌ Get habits failed: {habits_response.status_code}")
    
    # Test 5: Get Habit Progress
    print("\n5. Testing Habit Progress...")
    progress_response = requests.get(f"{BASE_URL}/get_habit_progress/{user_id}/{habit_id}")
    if progress_response.status_code == 200:
        progress_data = progress_response.json()
        print(f"✅ Habit progress retrieved!")
        print(f"   Current streak: {progress_data['current_streak']} days")
        print(f"   Success rate: {progress_data['success_rate']}%")
        print(f"   Total logs: {progress_data['total_logs']}")
    else:
        print(f"❌ Habit progress failed: {progress_response.status_code}")
    
    # Test 6: Dashboard Stats
    print("\n6. Testing Dashboard Statistics...")
    dashboard_response = requests.get(f"{BASE_URL}/api/users/{user_id}/dashboard")
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        print(f"✅ Dashboard stats retrieved!")
        print(f"   Total habits: {dashboard_data['total_habits']}")
        print(f"   Completed today: {dashboard_data['completed_today']}")
        print(f"   Weekly progress: {dashboard_data['weekly_progress']:.1f}%")
        print(f"   Longest streak: {dashboard_data['longest_streak']} days")
    else:
        print(f"❌ Dashboard stats failed: {dashboard_response.status_code}")
    
    # Test 7: Habit Stacking with Database
    print("\n7. Testing Habit Stacking with Database...")
    stack_response = requests.post(f"{BASE_URL}/stack_habits", 
                                  json={
                                      "current_habits": ["Make morning coffee", "Brush teeth"],
                                      "desired_habits": ["Read for 5 minutes", "Do push-ups"],
                                      "user_id": user_id
                                  })
    if stack_response.status_code == 200:
        stack_data = stack_response.json()
        created_stacks = stack_data.get('created_habits', [])
        print(f"✅ Habit stacks created and stored!")
        print(f"   Created {len(created_stacks)} stacked habits")
        if stack_data.get('habit_stacks'):
            first_stack = stack_data['habit_stacks'][0]
            print(f"   Example: {first_stack.get('stack_formula', '')[:60]}...")
    else:
        print(f"❌ Habit stacking failed: {stack_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 Database Integration Testing Complete!")
    print(f"\n📊 Database Location: data/habitbuilder.db")
    print(f"🌐 App URL: {BASE_URL}")
    print("\n✨ Your habits are now being stored in a real database!")

if __name__ == "__main__":
    try:
        test_database_integration()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the Flask app.")
        print("   Make sure the app is running: python app.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
