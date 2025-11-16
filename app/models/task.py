from app.extensions import db
from datetime import datetime


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    title = db.Column(db.String(255), nullable=False)



    date_added = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(),
    )

    streak = db.Column(db.Integer, nullable=False, default=0)

    # relationships
    user = db.relationship("User", back_populates="tasks")

    occurrences = db.relationship(
        "TaskOccurrences",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    completions = db.relationship(
        "TaskCompletion",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Task id={self.id} title={self.title!r} user_id={self.user_id}>"

class TaskOccurrences(db.Model):
    __tablename__ = "task_occurrences"

    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(
        db.Integer,
        db.ForeignKey("tasks.id"),
        nullable=False,
    )

    # Day of week: 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
    frequency = db.Column(db.String(3), nullable=False)
    
    next_due_at = db.Column(db.DateTime, nullable=False)

    # relationships
    task = db.relationship("Task", back_populates="occurrences")

    def __repr__(self):
        return f"<TaskOccurrences id={self.id} task_id={self.task_id} date={self.next_due_at}>"

class TaskCompletion(db.Model):
    __tablename__ = "task_completions"

    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(
        db.Integer,
        db.ForeignKey("tasks.id"),
        nullable=False,
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
    )

    # relationships
    task = db.relationship("Task", back_populates="completions")

    def __repr__(self):
        return f"<TaskCompletion id={self.id} task_id={self.task_id} at={self.completed_at}>"
