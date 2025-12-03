import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch

sys.path.append(os.path.abspath('backend'))

# We need to patch BEFORE importing TaskService if we want to affect the default argument?
# No, default argument is already evaluated.
# But we can test get_next_due_date by passing explicit date.

from app.services.task_service import TaskService

def test_logic(current_time, frequency, expected_day_name, description):
    print(f"--- {description} ---")
    print(f"Current Time (Simulated): {current_time}")
    print(f"Target Frequency: {frequency}")
    
    # We pass current_time as occurrence_due_date to simulate 'now'
    # But wait, get_next_due_date uses datetime.now() for 'today' calculation too.
    # So we MUST patch datetime.now()
    
    with patch('app.services.task_service.datetime') as mock_datetime:
        mock_datetime.now.return_value = current_time
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        try:
            # We pass current_time as occurrence_due_date to override the stale default
            next_due = TaskService.get_next_due_date(frequency, current_time)
            
            print(f"Result: {next_due}")
            print(f"Result Day: {next_due.strftime('%A')}")
            
            if next_due.strftime('%A').lower() != expected_day_name.lower():
                print(f"MISMATCH! Expected {expected_day_name}, got {next_due.strftime('%A')}")
            else:
                print("MATCH")
        except Exception as e:
            print(f"Error: {e}")
    print("")

# Case 1: Same Day (Tuesday -> Tuesday)
# If logic is <= 0, this will push to Next Tuesday.
tuesday = datetime(2023, 10, 10, 12, 0, 0)
test_logic(tuesday, 'tue', 'Tuesday', "Same Day (Tuesday -> Tuesday)")

# Case 2: Next Day (Tuesday -> Wednesday)
test_logic(tuesday, 'wed', 'Wednesday', "Next Day (Tuesday -> Wednesday)")

# Case 3: Server Ahead (Server Wed, User Tue -> User wants Tue)
# Server thinks it is Wednesday. User wants Tuesday.
# Should be Next Tuesday (since Tuesday is passed for server).
wednesday = datetime(2023, 10, 11, 3, 0, 0)
test_logic(wednesday, 'tue', 'Tuesday', "Server Ahead (Wed), Target Tue")

# Case 4: Server Ahead (Server Wed, User Tue -> User wants Wed (Tomorrow))
# Server thinks it is Wednesday. User wants Wednesday.
# If logic is <= 0, this will push to Next Wednesday.
# But user expects This Wednesday (Tomorrow).
test_logic(wednesday, 'wed', 'Wednesday', "Server Ahead (Wed), Target Wed")
