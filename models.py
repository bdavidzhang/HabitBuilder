"""
Database models for HabitBuilder app
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import json

db = SQLAlchemy()

class User(db.Model):
    """User model to store user information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # User preferences and settings
    main_goal = db.Column(db.Text, nullable=True)
    identity_shift = db.Column(db.Text, nullable=True)
    
    # Relationships
    habits = db.relationship('Habit', backref='user', lazy=True, cascade='all, delete-orphan')
    habit_logs = db.relationship('HabitLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'main_goal': self.main_goal,
            'identity_shift': self.identity_shift,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Habit(db.Model):
    """Habit model to store individual habits"""
    __tablename__ = 'habits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Habit details
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    two_minute_version = db.Column(db.Text, nullable=True)
    rationale = db.Column(db.Text, nullable=True)
    
    # Habit stacking
    anchor_habit = db.Column(db.String(200), nullable=True)  # What habit this is stacked on
    stack_formula = db.Column(db.Text, nullable=True)  # Complete stack formula
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    logs = db.relationship('HabitLog', backref='habit', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'two_minute_version': self.two_minute_version,
            'rationale': self.rationale,
            'anchor_habit': self.anchor_habit,
            'stack_formula': self.stack_formula,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class HabitLog(db.Model):
    """Habit log model to track daily habit completion"""
    __tablename__ = 'habit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id'), nullable=False)
    
    # Log details
    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    difficulty_rating = db.Column(db.Integer, nullable=True)  # 1-5 scale
    
    # Metadata
    logged_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Unique constraint to prevent duplicate logs for same habit on same day
    __table_args__ = (db.UniqueConstraint('user_id', 'habit_id', 'date', name='unique_habit_log'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'habit_id': self.habit_id,
            'date': self.date.isoformat() if self.date else None,
            'completed': self.completed,
            'notes': self.notes,
            'difficulty_rating': self.difficulty_rating,
            'logged_at': self.logged_at.isoformat() if self.logged_at else None
        }

class UserSession(db.Model):
    """Simple session management for users"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref='sessions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_token': self.session_token,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }

def init_db_tables(app):
    """Initialize the database tables (called from app.py)"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
