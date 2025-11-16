from .user import UserSchema
from .task import TaskSchema, TaskCompletionSchema

# Single / many schema instances
user_schema = UserSchema()
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
completion_schema = TaskCompletionSchema()
completions_schema = TaskCompletionSchema(many=True)

__all__ = [
    'UserSchema',
    'TaskSchema',
    'TaskCompletionSchema',
    'user_schema',
    'task_schema',
    'tasks_schema',
    'completion_schema',
    'completions_schema',
]
