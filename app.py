from flask import Flask, request, jsonify, render_template, session
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

# Database imports
from models import db, init_db_tables
from database_service import DatabaseService

app = Flask(__name__, static_folder='frontend/habit-builder-react/build', static_url_path='')
CORS(app)

# Database configuration - flexible for different environments
if os.getenv('DATABASE_URL'):
    # Production - use environment variable (Heroku, Railway, etc.)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
elif os.getenv('FLASK_ENV') == 'production':
    # Production with PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/habitbuilder'
else:
    # Development - SQLite in data directory
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'habitbuilder.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Initialize database
db.init_app(app)

# Create tables and default data
with app.app_context():
    db.create_all()
    
    # Create a default user for testing if none exists
    from models import User
    if not User.query.first():
        default_user = User(
            username='demo_user',
            email='demo@habitbuilder.com',
            main_goal='Build better habits',
            identity_shift='You are becoming someone who consistently builds positive habits'
        )
        db.session.add(default_user)
        db.session.commit()
        print(f"✅ Created default user: {default_user.username}")
    else:
        print("✅ Database already initialized")

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

# User management endpoints
@app.route('/api/users', methods=['POST'])
def create_or_get_user():
    """Create or get a user"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    user = DatabaseService.get_or_create_user(username, email)
    return jsonify(user.to_dict())

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user information"""
    from models import User
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())

@app.route('/decompose_goal', methods=['POST'])
def decompose_goal():
    data = request.get_json()
    user_goal = data.get('goal')
    user_id = data.get('user_id', 1)  # Default to user 1 for now

    if not user_goal:
        return jsonify({"error": "Goal not provided"}), 400

    # Get AI decomposition
    decomposed_habits = goal_decomposition(user_goal)
    
    # Update user's main goal and identity shift
    identity_shift = decomposed_habits.get('identity_shift')
    DatabaseService.update_user_goal(user_id, user_goal, identity_shift)
    
    # Create habits in database
    created_habits = []
    atomic_habits = decomposed_habits.get('atomic_habits', [])
    for habit_data in atomic_habits:
        habit = DatabaseService.create_habit_from_decomposition(user_id, habit_data)
        created_habits.append(habit.to_dict())
    
    # Return the original AI response plus database IDs
    response = decomposed_habits.copy()
    response['created_habits'] = created_habits
    
    return jsonify(response)

@app.route('/stack_habits', methods=['POST'])
def stack_habits():
    data = request.get_json()
    current_habits = data.get('current_habits')
    desired_habits = data.get('desired_habits')
    user_id = data.get('user_id', 1)  # Default to user 1 for now

    if not current_habits or not desired_habits:
        return jsonify({"error": "Current habits and desired habits must be provided"}), 400

    # Get AI habit stacking
    stacked_result = generate_habit_stacks(current_habits, desired_habits)
    
    # Create stacked habits in database
    created_habits = []
    habit_stacks = stacked_result.get('habit_stacks', [])
    for stack_data in habit_stacks:
        habit = DatabaseService.create_habit_stack(user_id, stack_data)
        created_habits.append(habit.to_dict())
    
    # Return the original AI response plus database IDs
    response = stacked_result.copy()
    response['created_habits'] = created_habits
    
    return jsonify(response)

# Database-powered habit tracking endpoints
@app.route('/track_habit', methods=['POST'])
def track_habit():
    """Track habit completion"""
    data = request.get_json()
    user_id = data.get('user_id', 1)  # Default to user 1 for now
    habit_id = data.get('habit_id')
    habit_name = data.get('habit_name')
    completed = data.get('completed', True)
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    notes = data.get('notes')
    difficulty_rating = data.get('difficulty_rating')
    
    # Get habit by ID or name
    if habit_id:
        from models import Habit
        habit = Habit.query.filter_by(user_id=user_id, id=habit_id).first()
    elif habit_name:
        habit = DatabaseService.get_habit_by_name(user_id, habit_name)
    else:
        return jsonify({"error": "Habit ID or name is required"}), 400
    
    if not habit:
        return jsonify({"error": "Habit not found"}), 404
    
    # Log the habit completion
    log = DatabaseService.log_habit_completion(
        user_id, habit.id, date, completed, notes, difficulty_rating
    )
    
    if log:
        return jsonify({
            "success": True,
            "message": f"Habit '{habit.name}' marked as {'completed' if completed else 'not completed'} for {date}",
            "log": log.to_dict()
        })
    else:
        return jsonify({"error": "Failed to log habit completion"}), 500

@app.route('/api/users/<int:user_id>/habits', methods=['GET'])
def get_user_habits(user_id):
    """Get all habits for a user"""
    habits = DatabaseService.get_user_habits(user_id)
    return jsonify([habit.to_dict() for habit in habits])

@app.route('/get_habit_progress/<int:user_id>/<int:habit_id>', methods=['GET'])
def get_habit_progress(user_id, habit_id):
    """Get progress for a specific habit"""
    days = request.args.get('days', 30, type=int)
    
    # Get habit info
    from models import Habit
    habit = Habit.query.filter_by(user_id=user_id, id=habit_id).first()
    if not habit:
        return jsonify({"error": "Habit not found"}), 404
    
    # Get progress data
    logs = DatabaseService.get_habit_progress(user_id, habit_id, days)
    current_streak = DatabaseService.get_current_streak(user_id, habit_id)
    success_rate = DatabaseService.get_success_rate(user_id, habit_id, days)
    
    return jsonify({
        "habit": habit.to_dict(),
        "current_streak": current_streak,
        "success_rate": round(success_rate, 1),
        "total_logs": len(logs),
        "logs": [log.to_dict() for log in logs[-10:]]  # Last 10 logs
    })

@app.route('/api/users/<int:user_id>/dashboard', methods=['GET'])
def get_dashboard_stats(user_id):
    """Get comprehensive dashboard statistics"""
    stats = DatabaseService.get_user_dashboard_stats(user_id)
    return jsonify(stats)

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