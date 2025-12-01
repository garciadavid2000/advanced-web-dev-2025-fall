from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth import exceptions
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from app.models import User, Task
from app.extensions import db
from flask import current_app


class CalendarService:
    """Service for Google Calendar API integration"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    # Category to Google Calendar color mapping
    CATEGORY_COLORS = {
        'General': '0',      # Graphite
        'Work': '1',         # Blueberry
        'Personal': '2',     # Sage
        'Health': '3',       # Flamingo
        'Finance': '4',      # Tangerine
        'Travel': '5',       # Banana
        'Entertainment': '6', # Peacock
        'Family': '7',       # Lavender
    }
    
    @staticmethod
    def get_calendar_credentials(user: User):
        """
        Get valid Google Calendar credentials from user's OAuth tokens.
        Refresh token if expired.
        """
        if not user.access_token:
            raise ValueError("User has no Google OAuth token")
        
        credentials = Credentials(
            token=user.access_token,
            refresh_token=user.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=current_app.config.get('GOOGLE_CLIENT_ID'),
            client_secret=current_app.config.get('GOOGLE_CLIENT_SECRET'),
            scopes=CalendarService.SCOPES
        )
        
        # Refresh if expired
        if user.is_token_expired():
            try:
                request = Request()
                credentials.refresh(request)
                
                # Update user's tokens
                user.access_token = credentials.token
                if credentials.refresh_token:
                    user.refresh_token = credentials.refresh_token
                user.token_expiry = datetime.now() + timedelta(seconds=3600)
                
                from app.services.user_service import UserService
                UserService.update_user_tokens(user)
            except Exception as e:
                raise ValueError(f"Failed to refresh token: {str(e)}")
        
        return credentials
    
    @staticmethod
    def create_event(user: User, title: str, due_date: datetime, description: str = None):
        """
        Create a calendar event for a task.
        
        Args:
            user: User object with valid OAuth tokens
            title: Event title
            due_date: Date/datetime for the event
            description: Optional event description
        
        Returns:
            event: Created Google Calendar event object
        """
        try:
            credentials = CalendarService.get_calendar_credentials(user)
            service = build('calendar', 'v3', credentials=credentials)
            
            # Create event object
            event = {
                'summary': title,
                'description': description or '',
                'start': {
                    'date' if isinstance(due_date, datetime.date) and not isinstance(due_date, datetime)
                        else 'dateTime': due_date.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'date' if isinstance(due_date, datetime.date) and not isinstance(due_date, datetime)
                        else 'dateTime': (due_date + timedelta(days=1)).isoformat() 
                        if isinstance(due_date, datetime.date) and not isinstance(due_date, datetime)
                        else (due_date + timedelta(hours=1)).isoformat(),
                    'timeZone': 'UTC',
                }
            }
            
            # If due_date is just a date, format appropriately
            if isinstance(due_date, datetime.date) and not isinstance(due_date, datetime):
                event['start'] = {'date': due_date.isoformat()}
                event['end'] = {'date': (due_date + timedelta(days=1)).isoformat()}
            
            # Insert event to calendar
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return created_event
            
        except Exception as e:
            raise ValueError(f"Failed to create calendar event: {str(e)}")
    
    @staticmethod
    def delete_calendar_events(user: User, service=None):
        """
        Delete all calendar events created by this app for the user.
        Uses a special marker in the description to identify app-created events.
        
        Args:
            user: User object with valid OAuth tokens
            service: Optional pre-built Google Calendar service
        
        Returns:
            dict: {deleted_count, errors}
        """
        try:
            if service is None:
                credentials = CalendarService.get_calendar_credentials(user)
                service = build('calendar', 'v3', credentials=credentials)
            
            results = {'deleted': 0, 'errors': []}
            
            # Get all events from primary calendar
            events_result = service.events().list(
                calendarId='primary',
                q='AppTask:',  # Search for events with AppTask marker
                maxResults=100
            ).execute()
            
            events = events_result.get('items', [])
            
            for event in events:
                try:
                    service.events().delete(
                        calendarId='primary',
                        eventId=event['id']
                    ).execute()
                    results['deleted'] += 1
                except Exception as delete_error:
                    results['errors'].append({
                        'event_id': event.get('id'),
                        'error': str(delete_error)
                    })
            
            return results
            
        except Exception as e:
            raise ValueError(f"Failed to delete calendar events: {str(e)}")
    
    @staticmethod
    def sync_tasks_to_calendar(user: User, tasks_by_date: dict):
        """
        Sync all tasks to user's Google Calendar (delete old events, then create new ones).
        
        Args:
            user: User object with valid OAuth tokens
            tasks_by_date: Dictionary of {date: [tasks]} from TaskService.get_user_tasks()
        
        Returns:
            dict: Summary of sync operation including deleted, created, and errors
        """
        results = {
            'deleted': 0,
            'success': 0,
            'failed': 0,
            'errors': [],
            'event_ids': []
        }
        
        try:
            credentials = CalendarService.get_calendar_credentials(user)
            service = build('calendar', 'v3', credentials=credentials)
            
            # Step 1: Delete all existing app-created events
            delete_results = CalendarService.delete_calendar_events(user, service)
            results['deleted'] = delete_results['deleted']
            results['errors'].extend(delete_results['errors'])
            
            # Step 2: Create new events from current tasks
            for date_str, tasks in tasks_by_date.items():
                for task in tasks:
                    try:
                        # Parse date string (format: YYYY-MM-DD)
                        task_date = datetime.strptime(str(date_str), '%Y-%m-%d').date()
                        
                        # Get task object to store google_event_id
                        task_obj = db.session.get(Task, task['task_id'])
                        category = task.get('category', 'General')
                        color_id = CalendarService.CATEGORY_COLORS.get(category, '0')
                        
                        event = {
                            'summary': task['title'],
                            'description': f"AppTask:{task['id']}",  # Marker for future deletion
                            'start': {'date': task_date.isoformat()},
                            'end': {'date': (task_date + timedelta(days=1)).isoformat()},
                            'colorId': color_id,
                        }
                        
                        created_event = service.events().insert(
                            calendarId='primary',
                            body=event
                        ).execute()
                        
                        # Store event ID on task for future reference
                        if task_obj:
                            task_obj.google_event_id = created_event.get('id')
                            db.session.commit()
                        
                        results['success'] += 1
                        results['event_ids'].append(created_event.get('id'))
                        
                    except Exception as task_error:
                        results['failed'] += 1
                        results['errors'].append({
                            'task': task.get('title', 'Unknown'),
                            'date': str(date_str),
                            'error': str(task_error)
                        })
            
            return results
            
        except Exception as e:
            raise ValueError(f"Failed to sync tasks to calendar: {str(e)}")
    
    @staticmethod
    def export_all_tasks_to_calendar(user: User, tasks_by_date: dict):
        """
        Export all tasks to user's Google Calendar.
        Now uses sync_tasks_to_calendar to prevent duplicates.
        
        Args:
            user: User object with valid OAuth tokens
            tasks_by_date: Dictionary of {date: [tasks]} from TaskService.get_user_tasks()
        
        Returns:
            dict: Summary of sync operation
        """
        return CalendarService.sync_tasks_to_calendar(user, tasks_by_date)
