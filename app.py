from flask import Flask, request, jsonify, render_template
import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add the parent directory to the sys.path to allow importing habit_builder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from habit_builder import goal_decomposition
from habit_stacker import generate_habit_stacks # Import the new function

app = Flask(__name__, static_folder='frontend/habit-builder-react/build', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

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

if __name__ == '__main__':
    app.run(debug=True)