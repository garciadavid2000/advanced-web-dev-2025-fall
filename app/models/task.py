from app.extensions import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    title = db.Column(db.String(255), nullable=False)
    frequency_cron = db.Column(db.String(255), nullable=False)

    next_due_at = db.Column(db.DateTime, nullable=False)
    last_completed_at = db.Column(db.DateTime)  # nullable: never completed yet

    date_added = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now(),
    )

    streak = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # relationships
    user = db.relationship("User", back_populates="tasks")

    completions = db.relationship(
        "TaskCompletion",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Task id={self.id} title={self.title!r} user_id={self.user_id}>"


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
