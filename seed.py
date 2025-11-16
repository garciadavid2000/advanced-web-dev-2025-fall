from datetime import datetime, timedelta
from models import db, User, Task, TaskCompletion
from app import create_app


def seed_data():
    app = create_app()
    with app.app_context():
        # Drop existing data (optional) and recreate tables
        db.drop_all()
        db.create_all()

        # Create users
        user1 = User(email="alice@example.com", name="Alice")
        user2 = User(email="bob@example.com", name="Bob")
        db.session.add_all([user1, user2])
        db.session.commit()

        # Create tasks for Alice
        task1 = Task(
            user_id=user1.id,
            title="Go to the gym",
            frequency_cron="0 7 * * *",  # daily at 7 AM
            next_due_at=datetime.utcnow() + timedelta(days=1),
            streak=3,
            last_completed_at=datetime.utcnow() - timedelta(days=1),
        )
        task2 = Task(
            user_id=user1.id,
            title="Watch lectures",
            frequency_cron="0 20 * * 1-5",  # weekdays at 8 PM
            next_due_at=datetime.utcnow(),
            streak=0,
            last_completed_at=None,
        )

        # Add to DB
        db.session.add_all([task1, task2])
        db.session.commit()

        # Add completions for task1
        for i in range(3):
            completion = TaskCompletion(
                task_id=task1.id,
                completed_at=datetime.utcnow() - timedelta(days=3 - i),
            )
            db.session.add(completion)

        # Create tasks for Bob
        task3 = Task(
            user_id=user2.id,
            title="Wash the dishes",
            frequency_cron="0 21 * * *",  # daily at 9 PM
            next_due_at=datetime.utcnow(),
            streak=5,
            last_completed_at=datetime.utcnow(),
        )

        db.session.add(task3)
        db.session.commit()

        # Add completions for Bob's task
        for i in range(5):
            completion = TaskCompletion(
                task_id=task3.id,
                completed_at=datetime.utcnow() - timedelta(days=5 - i),
            )
            db.session.add(completion)

        db.session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    seed_data()
