from app.extensions import db
from app.models import Task, TaskCompletion


class TaskService:
    """Business logic for task operations"""

    @staticmethod
    def create_task(user_id, title, frequency_cron, next_due_at):
        """Create a new task"""
        task = Task(
            user_id=user_id,
            title=title,
            frequency_cron=frequency_cron,
            next_due_at=next_due_at,
        )
        db.session.add(task)
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
        """Delete a task"""
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            return True
        return False

    @staticmethod
    def complete_task(task_id):
        """Mark a task as completed"""
        task = Task.query.get(task_id)
        if task:
            completion = TaskCompletion(task_id=task_id)
            db.session.add(completion)
            task.streak += 1
            db.session.commit()
            return completion
        return None
