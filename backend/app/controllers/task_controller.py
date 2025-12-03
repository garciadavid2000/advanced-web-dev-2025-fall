from flask import request
from app.controllers import task_bp
from app.services.task_service import TaskService
from app.schemas import task_schema
from app.utils.decorators import login_required
from app.utils.session_manager import get_current_user


@task_bp.route('', methods=['POST'])
@login_required
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        user = get_current_user()
        task = TaskService.create_task(
            user_id=user.id,
            title=data.get('title'),
            frequency=data.get('frequency'),
            category=data.get('category')
        )
        return task_schema.dump(task), 201
    except ValueError as e:
        return {"error": str(e)}, 400
    except Exception as e:
        return {"error": str(e)}, 400

@task_bp.route('<int:task_id>', methods=['PUT'])
@login_required
def update_task_title(task_id):
    """Update a task's title"""
    try:
        data = request.get_json()
        new_title = data.get('title')
        if not new_title:
            return {"error": "title is required"}, 400
        
        task = TaskService.update_task_name(get_current_user().id, task_id, new_title)
        if task:
            return task_schema.dump(task), 200
        return {"error": "Task not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 400

@task_bp.route('', methods=['GET'])
@login_required
def get_tasks():
    """Get all tasks for a user, grouped by due date"""
    try:
        user = get_current_user()
        grouped_tasks = TaskService.get_user_tasks(user.id)
        
        # Convert to JSON-serializable format
        result = {}
        for due_date, occurrences in grouped_tasks.items():
            # occurrences is already a list of dicts, just convert datetime to string
            result[str(due_date)] = [
                {
                    **occ,
                    'next_due_at': occ['next_due_at'].isoformat()
                }
                for occ in occurrences
            ]
        
        return result, 200
    except Exception as e:
        return {"error": str(e)}, 400


@task_bp.route('<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    try:
        if TaskService.delete_task(get_current_user().id, task_id):
            return {"message": "Task deleted successfully"}, 200
        return {"error": "Task not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 400


@task_bp.route('<int:occurrence_id>/complete', methods=['POST'])
@login_required
def complete_task(occurrence_id):
    """Mark a task as completed"""
    try:
        completion = TaskService.complete_task(get_current_user().id, occurrence_id)
        if completion:
            return {"message": "Task marked as completed"}, 200
        return {"error": "Task not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 400
