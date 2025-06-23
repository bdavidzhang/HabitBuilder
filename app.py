from flask import Flask, request, jsonify, render_template
import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from datetime import datetime

# Add the parent directory to the sys.path to allow importing habit_builder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from habit_builder import goal_decomposition
from habit_stacker import generate_habit_stacks # Import the new function
from reduce_friction import deconstruct_complex_habit, analyze_and_adjust_habit

app = Flask(__name__, static_folder='frontend/habit-builder-react/build', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        # For React router, return index.html for non-API routes
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/decompose_goal', methods=['POST'])
def decompose_goal():
    data = request.get_json()
    user_goal = data.get('goal')

    if not user_goal:
        return jsonify({"error": "Goal not provided"}), 400

    decomposed_habits = goal_decomposition(user_goal)
    return jsonify(decomposed_habits)

@app.route('/stack_habits', methods=['POST'])
def stack_habits():
    data = request.get_json()
    current_habits = data.get('current_habits')
    desired_habits = data.get('desired_habits')

    if not current_habits or not desired_habits:
        return jsonify({"error": "Current habits and desired habits must be provided"}), 400

    stacked_result = generate_habit_stacks(current_habits, desired_habits)
    return jsonify(stacked_result)

# Add habit tracking endpoints
@app.route('/track_habit', methods=['POST'])
def track_habit():
    """Track habit completion"""
    data = request.get_json()
    habit_name = data.get('habit_name')
    completed = data.get('completed', True)
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    if not habit_name:
        return jsonify({"error": "Habit name is required"}), 400
    
    # Here you could integrate with your agent.py or store in a database
    # For now, we'll return a success response
    return jsonify({
        "success": True,
        "message": f"Habit '{habit_name}' marked as {'completed' if completed else 'not completed'} for {date}"
    })

@app.route('/get_habit_progress/<habit_name>', methods=['GET'])
def get_habit_progress(habit_name):
    """Get progress for a specific habit"""
    # This would integrate with your agent.py or database
    # For now, return sample data
    return jsonify({
        "habit_name": habit_name,
        "current_streak": 5,
        "total_completions": 25,
        "success_rate": 83.3,
        "last_completed": "2025-06-22"
    })

@app.route('/reduce_friction', methods=['POST'])
def reduce_friction():
    """Get a simplified progression plan for a complex habit"""
    data = request.get_json()
    complex_habit = data.get('habit')
    
    if not complex_habit:
        return jsonify({"error": "Habit not provided"}), 400
    
    progression_plan = deconstruct_complex_habit(complex_habit)
    return jsonify(progression_plan)

@app.route('/adjust_habit', methods=['POST'])
def adjust_habit():
    """Get suggestions for a struggling habit"""
    data = request.get_json()
    habit = data.get('habit')
    history = data.get('history', [])
    
    if not habit:
        return jsonify({"error": "Habit not provided"}), 400
    
    suggestions = analyze_and_adjust_habit(habit, history)
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True, port=5001)