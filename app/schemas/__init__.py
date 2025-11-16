from .user import UserSchema
from .task import TaskSchema, TaskCompletionSchema, TaskOccurrencesSchema

# Single / many schema instances
user_schema = UserSchema()
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
completion_schema = TaskCompletionSchema()
completions_schema = TaskCompletionSchema(many=True)
occurrence_schema = TaskOccurrencesSchema()
occurrences_schema = TaskOccurrencesSchema(many=True)

__all__ = [
    'UserSchema',
    'TaskSchema',
    'TaskCompletionSchema',
    'TaskOccurrencesSchema',
    'user_schema',
    'task_schema',
    'tasks_schema',
    'completion_schema',
    'completions_schemas',
    'occurrence_schema',
    'occurrences_schema',
]
