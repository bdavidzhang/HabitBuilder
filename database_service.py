"""
Database service layer for HabitBuilder app
Handles all database operations and business logic
"""
from models import db, User, Habit, HabitLog, UserSession
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, and_, desc
from sqlalchemy.exc import IntegrityError
import uuid

class DatabaseService:
    """Service class to handle all database operations"""
    
    @staticmethod
    def get_or_create_user(username, email=None):
        """Get existing user or create a new one"""
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, email=email)
            db.session.add(user)
            db.session.commit()
        return user
    
    @staticmethod
    def create_habit_from_decomposition(user_id, habit_data):
        """Create a habit from goal decomposition data"""
        habit = Habit(
            user_id=user_id,
            name=habit_data.get('habit_name'),
            description=habit_data.get('habit_name'),
            two_minute_version=habit_data.get('two_minute_version'),
            rationale=habit_data.get('rationale')
        )
        db.session.add(habit)
        db.session.commit()
        return habit
    
    @staticmethod
    def create_habit_stack(user_id, stack_data):
        """Create a habit from habit stacking data"""
        habit = Habit(
            user_id=user_id,
            name=stack_data.get('new_habit'),
            anchor_habit=stack_data.get('anchor_habit'),
            stack_formula=stack_data.get('stack_formula'),
            rationale=stack_data.get('reasoning')
        )
        db.session.add(habit)
        db.session.commit()
        return habit
    
    @staticmethod
    def log_habit_completion(user_id, habit_id, date, completed, notes=None, difficulty_rating=None):
        """Log habit completion for a specific date"""
        try:
            # Parse date if it's a string
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Check if log already exists
            existing_log = HabitLog.query.filter_by(
                user_id=user_id,
                habit_id=habit_id,
                date=date
            ).first()
            
            if existing_log:
                # Update existing log
                existing_log.completed = completed
                existing_log.notes = notes
                existing_log.difficulty_rating = difficulty_rating
                existing_log.logged_at = datetime.now(timezone.utc)
                log = existing_log
            else:
                # Create new log
                log = HabitLog(
                    user_id=user_id,
                    habit_id=habit_id,
                    date=date,
                    completed=completed,
                    notes=notes,
                    difficulty_rating=difficulty_rating
                )
                db.session.add(log)
            
            db.session.commit()
            return log
            
        except IntegrityError:
            db.session.rollback()
            return None
    
    @staticmethod
    def get_user_habits(user_id, active_only=True):
        """Get all habits for a user"""
        query = Habit.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Habit.created_at.desc()).all()
    
    @staticmethod
    def get_habit_progress(user_id, habit_id, days=30):
        """Get habit progress for the last N days"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        logs = HabitLog.query.filter(
            and_(
                HabitLog.user_id == user_id,
                HabitLog.habit_id == habit_id,
                HabitLog.date >= start_date,
                HabitLog.date <= end_date
            )
        ).order_by(HabitLog.date.desc()).all()
        
        return logs
    
    @staticmethod
    def get_current_streak(user_id, habit_id):
        """Calculate current streak for a habit"""
        today = datetime.now().date()
        streak = 0
        
        # Get logs in reverse chronological order
        logs = HabitLog.query.filter_by(
            user_id=user_id,
            habit_id=habit_id
        ).order_by(desc(HabitLog.date)).all()
        
        # Calculate streak from most recent completed day
        current_date = today
        for log in logs:
            if log.date == current_date and log.completed:
                streak += 1
                current_date -= timedelta(days=1)
            elif log.date == current_date and not log.completed:
                break
            elif log.date < current_date:
                # Skip days without logs, but stop if we find a non-completed day
                if log.completed:
                    # There's a gap, but this day was completed
                    # For now, we'll break the streak on gaps
                    break
                else:
                    break
        
        return streak
    
    @staticmethod
    def get_success_rate(user_id, habit_id, days=30):
        """Calculate success rate for a habit over the last N days"""
        logs = DatabaseService.get_habit_progress(user_id, habit_id, days)
        if not logs:
            return 0.0
        
        completed_days = sum(1 for log in logs if log.completed)
        return (completed_days / len(logs)) * 100
    
    @staticmethod
    def get_user_dashboard_stats(user_id):
        """Get comprehensive dashboard statistics for a user"""
        habits = DatabaseService.get_user_habits(user_id)
        today = datetime.now().date()
        
        stats = {
            'total_habits': len(habits),
            'completed_today': 0,
            'habits_with_streaks': {},
            'weekly_progress': 0,
            'longest_streak': 0
        }
        
        total_possible_today = 0
        total_completed_today = 0
        weekly_completions = 0
        weekly_possible = 0
        
        for habit in habits:
            # Today's completion
            today_log = HabitLog.query.filter_by(
                user_id=user_id,
                habit_id=habit.id,
                date=today
            ).first()
            
            total_possible_today += 1
            if today_log and today_log.completed:
                total_completed_today += 1
            
            # Current streak
            streak = DatabaseService.get_current_streak(user_id, habit.id)
            stats['habits_with_streaks'][habit.name] = streak
            stats['longest_streak'] = max(stats['longest_streak'], streak)
            
            # Weekly progress
            week_ago = today - timedelta(days=7)
            weekly_logs = HabitLog.query.filter(
                and_(
                    HabitLog.user_id == user_id,
                    HabitLog.habit_id == habit.id,
                    HabitLog.date >= week_ago,
                    HabitLog.date <= today
                )
            ).all()
            
            weekly_possible += 7  # 7 days per habit
            weekly_completions += sum(1 for log in weekly_logs if log.completed)
        
        stats['completed_today'] = total_completed_today
        stats['weekly_progress'] = (weekly_completions / weekly_possible * 100) if weekly_possible > 0 else 0
        
        return stats
    
    @staticmethod
    def update_user_goal(user_id, main_goal, identity_shift=None):
        """Update user's main goal and identity shift"""
        user = User.query.get(user_id)
        if user:
            user.main_goal = main_goal
            if identity_shift:
                user.identity_shift = identity_shift
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
        return user
    
    @staticmethod
    def deactivate_habit(user_id, habit_id):
        """Deactivate a habit instead of deleting it"""
        habit = Habit.query.filter_by(user_id=user_id, id=habit_id).first()
        if habit:
            habit.is_active = False
            habit.updated_at = datetime.now(timezone.utc)
            db.session.commit()
        return habit
    
    @staticmethod
    def get_habit_by_name(user_id, habit_name):
        """Get a habit by name for a specific user"""
        return Habit.query.filter_by(
            user_id=user_id,
            name=habit_name,
            is_active=True
        ).first()
