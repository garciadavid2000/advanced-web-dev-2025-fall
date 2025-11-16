from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from app.models import Task, TaskCompletion
from app.extensions import db


class TaskCompletionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TaskCompletion
        sqla_session = db.session
        load_instance = True
        include_fk = True  # include task_id

    # Explicit datetime formatting (optional, but nice)
    completed_at = auto_field(format="%Y-%m-%dT%H:%M:%S")


class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        sqla_session = db.session
        load_instance = True
        include_fk = True  # include user_id

    # Datetime fields formatted as ISO strings
    next_due_at = auto_field(format="%Y-%m-%dT%H:%M:%S")
    last_completed_at = auto_field(format="%Y-%m-%dT%H:%M:%S")

    # If you want nested completions in the task JSON, uncomment this:
    # completions = fields.Nested(TaskCompletionSchema, many=True)
