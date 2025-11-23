import pytest
import json
from datetime import datetime, timedelta
from app.models.task import Task, TaskOccurrences, TaskCompletion
from app.extensions import db


class TestTaskEndpoints:
    """Comprehensive tests for all task endpoints."""
    
    # =====================
    # POST /tasks - CREATE
    # =====================
    
    def test_create_task_single_frequency(self, authenticated_client, test_user, app):
        """Test creating a task with a single frequency."""
        response = authenticated_client.post(
            '/tasks',
            json={
                'user_id': test_user['id'],
                'title': 'Morning Jog',
                'frequency': ['mon']
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'Morning Jog'
        assert data['user_id'] == test_user['id']
        
        with app.app_context():
            task = Task.query.filter_by(user_id=test_user['id']).first()
            assert task is not None
            assert task.title == 'Morning Jog'
            assert len(task.occurrences) == 1
    
    
    def test_create_task_multiple_frequencies(self, authenticated_client, test_user, app):
        """Test creating a task with multiple frequencies (multi-day)."""
        response = authenticated_client.post(
            '/tasks',
            json={
                'user_id': test_user['id'],
                'title': 'Gym Session',
                'frequency': ['mon', 'wed', 'fri']
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['title'] == 'Gym Session'
        
        with app.app_context():
            task = Task.query.filter_by(user_id=test_user['id']).first()
            assert len(task.occurrences) == 3
            frequencies = {occ.frequency for occ in task.occurrences}
            assert frequencies == {'mon', 'wed', 'fri'}
    
    
    def test_create_task_missing_title(self, authenticated_client, test_user):
        """Test creating a task without a title fails."""
        response = authenticated_client.post(
            '/tasks',
            json={
                'user_id': test_user['id'],
                'frequency': ['mon']
            }
        )
        
        assert response.status_code == 400
    
    
    def test_create_task_missing_frequency(self, authenticated_client, test_user):
        """Test creating a task without frequency fails."""
        response = authenticated_client.post(
            '/tasks',
            json={
                'user_id': test_user['id'],
                'title': 'Some Task'
            }
        )
        
        assert response.status_code == 400
    
    
    def test_create_task_invalid_frequency(self, authenticated_client, test_user):
        """Test creating a task with invalid frequency day."""
        response = authenticated_client.post(
            '/tasks',
            json={
                'user_id': test_user['id'],
                'title': 'Some Task',
                'frequency': ['invalid_day']
            }
        )
        
        assert response.status_code == 400
    
    
    def test_create_task_initializes_streak(self, authenticated_client, test_user, app):
        """Test that newly created tasks have streak initialized to 0."""
        response = authenticated_client.post(
            '/tasks',
            json={
                'user_id': test_user['id'],
                'title': 'Streak Task',
                'frequency': ['tue']
            }
        )
        
        assert response.status_code == 201
        
        with app.app_context():
            task = Task.query.filter_by(user_id=test_user['id']).first()
            assert task.streak == 0
    
    
    # =====================
    # GET /tasks - RETRIEVE
    # =====================
    
    def test_get_tasks_empty(self, authenticated_client, test_user):
        """Test retrieving tasks when user has none."""
        response = authenticated_client.get(
            f'/tasks?user_id={test_user['id']}'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == {}
    
    
    def test_get_tasks_groups_by_date(self, authenticated_client, test_user, app):
        """Test that tasks are grouped by due date."""
        # Create a task
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Test Task')
            db.session.add(task)
            db.session.flush()
            
            # Create occurrence with specific due date
            tomorrow = datetime.now() + timedelta(days=1)
            occurrence = TaskOccurrences(
                task_id=task.id,
                frequency='mon',
                next_due_at=tomorrow
            )
            db.session.add(occurrence)
            db.session.commit()
        
        response = authenticated_client.get(
            f'/tasks?user_id={test_user['id']}'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) > 0
        
        # Data should be grouped by date string
        for date_str, occurrences in data.items():
            assert isinstance(occurrences, list)
            for occ in occurrences:
                assert 'title' in occ
                assert 'streak' in occ
    
    
    def test_get_tasks_returns_correct_structure(self, authenticated_client, test_user, app):
        """Test that returned tasks have correct structure."""
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Structured Task')
            db.session.add(task)
            db.session.flush()
            
            occurrence = TaskOccurrences(
                task_id=task.id,
                frequency='tue',
                next_due_at=datetime.now()
            )
            db.session.add(occurrence)
            db.session.commit()
        
        response = authenticated_client.get(
            f'/tasks?user_id={test_user['id']}'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        for date_str, occurrences in data.items():
            for occ in occurrences:
                assert 'id' in occ  # task occurrence id
                assert 'title' in occ
                assert 'streak' in occ
                assert 'frequency' in occ
                assert 'next_due_at' in occ
    
    
    def test_get_tasks_missing_user_id(self, authenticated_client):
        """Test that get tasks requires user_id."""
        response = authenticated_client.get('/tasks')
        
        assert response.status_code == 400
    
    
    def test_get_tasks_only_own_tasks(self, authenticated_client, test_user, second_test_user, app):
        """Test that users only see their own tasks."""
        with app.app_context():
            # Create task for first user
            task1 = Task(user_id=test_user['id'], title='User 1 Task')
            db.session.add(task1)
            db.session.flush()
            
            occ1 = TaskOccurrences(task_id=task1.id, frequency='mon', next_due_at=datetime.now())
            db.session.add(occ1)
            
            # Create task for second user
            task2 = Task(user_id=second_test_user['id'], title='User 2 Task')
            db.session.add(task2)
            db.session.flush()
            
            occ2 = TaskOccurrences(task_id=task2.id, frequency='tue', next_due_at=datetime.now())
            db.session.add(occ2)
            db.session.commit()
        
        response = authenticated_client.get(
            f'/tasks?user_id={test_user['id']}'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify only user 1's tasks appear
        for date_str, occurrences in data.items():
            for occ in occurrences:
                assert occ['title'] == 'User 1 Task'
    
    
    # =====================
    # PUT /tasks/<id> - UPDATE
    # =====================
    
    def test_update_task_title(self, authenticated_client, test_user, app):
        """Test updating a task's title."""
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Old Title')
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = authenticated_client.put(
            f'/tasks/{task_id}',
            json={'title': 'New Title'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['title'] == 'New Title'
        
        with app.app_context():
            task = Task.query.get(task_id)
            assert task.title == 'New Title'
    
    
    def test_update_nonexistent_task(self, authenticated_client):
        """Test updating a task that doesn't exist."""
        response = authenticated_client.put(
            '/tasks/99999',
            json={'title': 'New Title'}
        )
        
        assert response.status_code == 404
    
    
    def test_update_task_missing_title(self, authenticated_client, test_user, app):
        """Test updating a task without providing title fails."""
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Original Title')
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = authenticated_client.put(
            f'/tasks/{task_id}',
            json={}
        )
        
        assert response.status_code == 400
    
    
    def test_update_task_empty_title(self, authenticated_client, test_user, app):
        """Test updating a task with empty title fails."""
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Original Title')
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = authenticated_client.put(
            f'/tasks/{task_id}',
            json={'title': ''}
        )
        
        assert response.status_code == 400
    
    
    # =====================
    # DELETE /tasks/<id> - DELETE
    # =====================
    
    def test_delete_task(self, authenticated_client, test_user, app):
        """Test deleting a task."""
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Task to Delete')
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = authenticated_client.delete(f'/tasks/{task_id}')
        
        assert response.status_code == 200
        
        with app.app_context():
            task = Task.query.get(task_id)
            assert task is None
    
    
    def test_delete_task_cascades_occurrences(self, authenticated_client, test_user, app):
        """Test that deleting a task cascades to occurrences."""
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Task with Occurrences')
            db.session.add(task)
            db.session.flush()
            
            for frequency in ['mon', 'wed', 'fri']:
                occ = TaskOccurrences(task_id=task.id, frequency=frequency, next_due_at=datetime.now())
                db.session.add(occ)
            
            db.session.commit()
            task_id = task.id
            
            # Verify occurrences exist
            assert TaskOccurrences.query.filter_by(task_id=task_id).count() == 3
        
        response = authenticated_client.delete(f'/tasks/{task_id}')
        
        assert response.status_code == 200
        
        with app.app_context():
            # Verify all occurrences are deleted
            assert TaskOccurrences.query.filter_by(task_id=task_id).count() == 0
    
    
    def test_delete_task_cascades_completions(self, authenticated_client, test_user, app):
        """Test that deleting a task cascades to completions."""
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Task with Completions')
            db.session.add(task)
            db.session.flush()
            
            completion = TaskCompletion(task_id=task.id)
            db.session.add(completion)
            db.session.commit()
            
            task_id = task.id
            assert TaskCompletion.query.filter_by(task_id=task_id).count() == 1
        
        response = authenticated_client.delete(f'/tasks/{task_id}')
        
        assert response.status_code == 200
        
        with app.app_context():
            assert TaskCompletion.query.filter_by(task_id=task_id).count() == 0
    
    
    def test_delete_nonexistent_task(self, authenticated_client):
        """Test deleting a task that doesn't exist."""
        response = authenticated_client.delete('/tasks/99999')
        
        assert response.status_code == 404
    
    
    # =====================
    # POST /tasks/<occurrence_id>/complete - MARK COMPLETE
    # =====================
    
    def test_complete_task_occurrence(self, authenticated_client, test_user, app):
        """Test marking a task occurrence as completed."""
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Completable Task')
            db.session.add(task)
            db.session.flush()
            
            occurrence = TaskOccurrences(
                task_id=task.id,
                frequency='mon',
                next_due_at=datetime.now() - timedelta(days=1)  # Past occurrence
            )
            db.session.add(occurrence)
            db.session.commit()
            
            task_id = task.id
            occurrence_id = occurrence.id
        
        response = authenticated_client.post(
            f'/tasks/{occurrence_id}/complete'
        )
        
        assert response.status_code == 200
        
        with app.app_context():
            completion = TaskCompletion.query.filter_by(task_id=task_id).first()
            assert completion is not None
    
    
    def test_complete_task_creates_next_occurrence(self, authenticated_client, test_user, app):
        """Test that completing a task creates the next occurrence."""
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Task for Next Occurrence')
            db.session.add(task)
            db.session.flush()
            
            occurrence = TaskOccurrences(
                task_id=task.id,
                frequency='mon',
                next_due_at=datetime.now()
            )
            db.session.add(occurrence)
            db.session.commit()
            
            task_id = task.id
            occurrence_id = occurrence.id
            initial_count = TaskOccurrences.query.filter_by(task_id=task_id).count()
        
        response = authenticated_client.post(
            f'/tasks/{occurrence_id}/complete'
        )
        
        assert response.status_code == 200
        
        with app.app_context():
            # Get the updated occurrence to verify it was modified
            occ = TaskOccurrences.query.get(occurrence_id)
            # Next due date should be updated to a future date
            assert occ.next_due_at > datetime.now()
    
    
    def test_complete_task_increments_streak_if_early(self, authenticated_client, test_user, app):
        """Test that completing early increments streak."""
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Streak Task', streak=5)
            db.session.add(task)
            db.session.flush()
            
            # Create occurrence due in the future (completing early)
            occurrence = TaskOccurrences(
                task_id=task.id,
                frequency='fri',
                next_due_at=datetime.now() + timedelta(days=3)
            )
            db.session.add(occurrence)
            db.session.commit()
            
            task_id = task.id
            occurrence_id = occurrence.id
        
        response = authenticated_client.post(
            f'/tasks/{occurrence_id}/complete'
        )
        
        assert response.status_code == 200
        
        with app.app_context():
            task = Task.query.get(task_id)
            # Streak should increment by 1
            assert task.streak == 6
    
    
    def test_complete_task_resets_streak_if_late(self, authenticated_client, test_user, app):
        """Test that completing late resets streak to 1."""
        with app.app_context():
            task = Task(user_id=test_user['id'], title='Late Streak Task', streak=10)
            db.session.add(task)
            db.session.flush()
            
            # Create occurrence due in the past (completing late)
            occurrence = TaskOccurrences(
                task_id=task.id,
                frequency='mon',
                next_due_at=datetime.now() - timedelta(days=2)
            )
            db.session.add(occurrence)
            db.session.commit()
            
            task_id = task.id
            occurrence_id = occurrence.id
        
        response = authenticated_client.post(
            f'/tasks/{occurrence_id}/complete'
        )
        
        assert response.status_code == 200
        
        with app.app_context():
            task = Task.query.get(task_id)
            # Streak should reset to 1
            assert task.streak == 1
    
    
    def test_complete_nonexistent_task(self, authenticated_client):
        """Test completing a nonexistent task."""
        response = authenticated_client.post(
            '/tasks/99999/complete'
        )
        
        assert response.status_code == 404
    
    
    def test_complete_nonexistent_occurrence(self, authenticated_client, test_user, app):
        """Test completing with nonexistent occurrence_id."""
        response = authenticated_client.post(
            '/tasks/99999/complete'
        )
        
        assert response.status_code == 404
