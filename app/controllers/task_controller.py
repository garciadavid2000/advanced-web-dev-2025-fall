from flask import request, jsonify
from app.controllers import task_bp
from app.services.task_service import TaskService
from app.schemas import task_schema, tasks_schema


@task_bp.route('', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        task = TaskService.create_task(
            user_id=data.get('user_id'),
            title=data.get('title'),
            frequency_cron=data.get('frequency_cron'),
            next_due_at=data.get('next_due_at')
        )
        return task_schema.dump(task), 201
    except Exception as e:
        return {"error": str(e)}, 400


@task_bp.route('', methods=['GET'])
def get_tasks():
    """Get all tasks for a user"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return {"error": "user_id is required"}, 400
        
        tasks = TaskService.get_user_tasks(user_id)
        return tasks_schema.dump(tasks), 200
    except Exception as e:
        return {"error": str(e)}, 400


@task_bp.route('<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        if TaskService.delete_task(task_id):
            return {"message": "Task deleted successfully"}, 200
        return {"error": "Task not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 400


@task_bp.route('<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark a task as completed"""
    try:
        completion = TaskService.complete_task(task_id)
        if completion:
            return {"message": "Task marked as completed"}, 200
        return {"error": "Task not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 400
