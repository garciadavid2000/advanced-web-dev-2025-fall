from app.extensions import db
from app.models import Task, TaskCompletion, TaskOccurrences
from datetime import datetime, timedelta


class TaskService:
    """Business logic for task operations"""
    
    # Map day names to weekday numbers (0=Monday, 6=Sunday)
    DAY_MAPPING = {
        'mon': 0,
        'tue': 1,
        'wed': 2,
        'thu': 3,
        'fri': 4,
        'sat': 5,
        'sun': 6,
    }

    @staticmethod
    def get_next_due_date(frequency):
        """Calculate next due date based on day of week"""
        if frequency.lower() not in TaskService.DAY_MAPPING:
            raise ValueError(f"Invalid frequency. Must be one of: {', '.join(TaskService.DAY_MAPPING.keys())}")
        
        target_weekday = TaskService.DAY_MAPPING[frequency.lower()]
        today = datetime.now()
        current_weekday = today.weekday()
        
        # Calculate days until target day
        days_ahead = target_weekday - current_weekday
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        next_due = today + timedelta(days=days_ahead)
        # Set to end of day
        return next_due.replace(hour=23, minute=59, second=59, microsecond=999999)

    @staticmethod
    def create_task(user_id, title, frequency):
        """Create a new task with one or more frequencies
        
        Args:
            user_id: User ID
            title: Task title
            frequency: Single day string (e.g., 'mon') or list of days (e.g., ['mon', 'wed', 'fri'])
        """
        # Convert single frequency to list for uniform processing
        frequencies = frequency if isinstance(frequency, list) else [frequency]
        
        # Validate all frequencies
        for freq in frequencies:
            if freq.lower() not in TaskService.DAY_MAPPING:
                raise ValueError(f"Invalid frequency: {freq}. Must be one of: {', '.join(TaskService.DAY_MAPPING.keys())}")
        
        # Create the main task
        task = Task(
            user_id=user_id,
            title=title,
        )
        db.session.add(task)
        db.session.flush()  # Get the task ID without committing
        
        # Create occurrences for each frequency
        for freq in frequencies:
            next_due_at = TaskService.get_next_due_date(freq)
            occurrence = TaskOccurrences(
                task_id=task.id,
                frequency=freq.lower(),
                next_due_at=next_due_at,
            )
            db.session.add(occurrence)
        
        db.session.commit()
        return task

    @staticmethod
    def get_task(task_id):
        """Get a task by ID"""
        return Task.query.get(task_id)

    @staticmethod
    def get_user_tasks(user_id):
        """Get all tasks for a user"""
        return Task.query.filter_by(user_id=user_id).all()

    @staticmethod
    def delete_task(task_id):
        """Delete a task and all its occurrences"""
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            return True
        return False

    @staticmethod
    def complete_task(task_id):
        """Mark a task as completed and create next occurrence"""
        task = Task.query.get(task_id)
        if not task:
            return None
        
        # Get the current occurrence
        current_occurrence = TaskOccurrences.query.filter_by(task_id=task_id).order_by(
            TaskOccurrences.next_due_at.desc()
        ).first()
        
        if not current_occurrence:
            return None
        
        # Create completion record
        completion = TaskCompletion(task_id=task_id)
        db.session.add(completion)
        
        # Check if completed before due date
        now = datetime.now()
        if now < current_occurrence.next_due_at:
            # Completed early - increment streak
            task.streak += 1
        else:
            # Completed on or after due date - reset streak
            task.streak = 1
        
        # Create next occurrence
        next_due_at = TaskService.get_next_due_date(current_occurrence.frequency)
        next_occurrence = TaskOccurrences(
            task_id=task_id,
            frequency=current_occurrence.frequency,
            next_due_at=next_due_at,
        )
        db.session.add(next_occurrence)
        db.session.commit()
        return completion
