export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

/**
 * Get the stored JWT token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('authToken');
}

/**
 * Create headers with JWT token in Authorization header if available
 */
function getAuthHeaders(): HeadersInit {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
}

export interface User {
  id: number;
  email: string;
  name: string;
  google_id: string;
  created_at: string;
}

export interface TaskOccurrence {
  id: number;
  task_id: number;
  frequency: string;
  next_due_at: string;
  title: string;
  streak: number;
}

export interface TasksByDate {
  [date: string]: TaskOccurrence[];
}

export class UnauthorizedError extends Error {
  constructor(message: string = 'Unauthorized') {
    super(message);
    this.name = 'UnauthorizedError';
  }
}

/**
 * Fetch current user information
 * Uses the session to determine the current user ID
 */
export async function fetchCurrentUser(): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/users/current`, {
    credentials: 'include',
    headers: getAuthHeaders(),
  });

  if (response.status === 401) {
    throw new UnauthorizedError('Not authenticated');
  }

  if (!response.ok) {
    throw new Error('Failed to fetch user data');
  }

  return response.json();
}

/**
 * Fetch all tasks for a user, grouped by due date
 */
export async function fetchUserTasks(userId: number): Promise<TasksByDate> {
  const response = await fetch(`${API_BASE_URL}/tasks?user_id=${userId}`, {
    credentials: 'include',
    headers: getAuthHeaders(),
  });

  if (response.status === 401) {
    throw new UnauthorizedError('Not authenticated');
  }

  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }

  return response.json();
}

/**
 * Mark a task occurrence as complete
 * @param occurrenceId The ID of the task occurrence to complete
 */
export async function completeTask(occurrenceId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/tasks/${occurrenceId}/complete`, {
    method: 'POST',
    credentials: 'include',
    headers: getAuthHeaders(),
  });

  if (response.status === 401) {
    throw new UnauthorizedError('Not authenticated');
  }

  if (!response.ok) {
    throw new Error('Failed to complete task');
  }
}

/**
 * Determine the earliest due date for a specific task
 * @param tasks All tasks grouped by date
 * @param taskId The task ID to find the earliest occurrence for
 */
export function getEarliestDueDate(tasks: TasksByDate, taskId: number): string | null {
  const dates = Object.keys(tasks).sort();

  for (const date of dates) {
    const tasksOnDate = tasks[date];
    if (tasksOnDate.some((t) => t.task_id === taskId)) {
      return date;
    }
  }

  return null;
}

/**
 * Check if a task occurrence can be completed (is the earliest occurrence of that task)
 */
export function canCompleteTask(
  tasks: TasksByDate,
  taskId: number,
  currentDate: string
): boolean {
  const earliestDate = getEarliestDueDate(tasks, taskId);
  return earliestDate === currentDate;
}

/**
 * Export all tasks to Google Calendar
 */
export async function exportToCalendar(): Promise<{
  message: string;
  success: number;
  failed: number;
  errors: Array<{ task: string; date: string; error: string }>;
  event_ids: string[];
}> {
  const response = await fetch(`${API_BASE_URL}/auth/calendar/export`, {
    method: 'POST',
    credentials: 'include',
    headers: getAuthHeaders(),
  });

  if (response.status === 401) {
    throw new UnauthorizedError('Not authenticated');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to export tasks to calendar');
  }

  return response.json();
}

