'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from './components/Sidebar';
import TaskDateGroup from './components/TaskDateGroup';
import NewTaskModal from './components/NewTaskModal';
import EditTaskModal from './components/EditTaskModal';
import {
  fetchCurrentUser,
  fetchUserTasks,
  completeTask,
  User,
  TasksByDate,
} from '@/apis/api';

export default function MainPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<TasksByDate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completingTaskId, setCompletingTaskId] = useState<number | null>(null);

  // Modal states
  const [showNewTaskModal, setShowNewTaskModal] = useState(false);
  const [showEditTaskModal, setShowEditTaskModal] = useState(false);
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editingTaskTitle, setEditingTaskTitle] = useState('');

  // Fetch user and tasks on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch current user
        const userData = await fetchCurrentUser();
        setUser(userData);

        // Fetch user's tasks
        const tasksData = await fetchUserTasks(userData.id);
        setTasks(tasksData);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An error occurred';
        console.error('Error loading data:', err);

        // If UnauthorizedError, redirect to sign-in (unless in test mode)
        if (err instanceof Error && err.name === 'UnauthorizedError') {
          if (process.env.NEXT_PUBLIC_TEST_MODE !== 'true') {
            router.push('/signin');
          } else {
            setError('Test mode: Authentication failed. Ensure backend test-login endpoint is available.');
          }
        } else {
          setError(errorMessage);
        }
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [router]);

  const handleCompleteTask = async (occurrenceId: number, taskId: number) => {
    try {
      setCompletingTaskId(occurrenceId);

      // Call the complete task endpoint
      await completeTask(occurrenceId);

      // Refetch tasks after completion
      if (user) {
        const updatedTasks = await fetchUserTasks(user.id);
        setTasks(updatedTasks);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete task');
      console.error('Error completing task:', err);
    } finally {
      setCompletingTaskId(null);
    }
  };

  const handleNewTask = () => {
    setShowNewTaskModal(true);
  };

  const handleTaskCreated = async () => {
    // Refetch tasks after creation
    if (user) {
      const updatedTasks = await fetchUserTasks(user.id);
      setTasks(updatedTasks);
    }
  };

  const handleEditTask = (taskId: number, currentTitle: string) => {
    setEditingTaskId(taskId);
    setEditingTaskTitle(currentTitle);
    setShowEditTaskModal(true);
  };

  const handleTaskUpdated = async () => {
    // Refetch tasks after update
    if (user) {
      const updatedTasks = await fetchUserTasks(user.id);
      setTasks(updatedTasks);
    }
  };

  // Show loading state
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#FAF9F7]">
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-[#D97757]/10 flex items-center justify-center">
            <svg className="w-6 h-6 text-[#D97757] animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <p className="text-gray-600 font-medium">Loading your tasks...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#FAF9F7]">
        <div className="text-center max-w-md px-6">
          <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-red-50 flex items-center justify-center">
            <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Something went wrong</h2>
          <p className="text-gray-500 mb-6">
            {error || 'Failed to load user data'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex items-center gap-2 bg-[#D97757] hover:bg-[#C4684A] text-white font-medium py-2.5 px-5 rounded-xl shadow-sm"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Try again
          </button>
        </div>
      </div>
    );
  }

  // Main page layout
  return (
    <div className="flex h-screen bg-[#FAF9F7]">
      <Sidebar userName={user.name} onNewTask={handleNewTask} />

      <main className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto p-8">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900">Your Tasks</h1>
            <p className="text-gray-500 mt-1">Stay on track with your daily habits</p>
          </div>

          {tasks && Object.keys(tasks).length > 0 ? (
            <div>
              {Object.entries(tasks).map(([date, tasksOnDate]) => (
                <TaskDateGroup
                  key={date}
                  date={date}
                  tasks={tasksOnDate}
                  allTasks={tasks}
                  onCompleteTask={handleCompleteTask}
                  onEditTask={handleEditTask}
                  loadingTaskId={completingTaskId || undefined}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-16">
              <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gray-100 flex items-center justify-center">
                <svg className="w-10 h-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No tasks yet</h3>
              <p className="text-gray-500 mb-6 max-w-sm mx-auto">
                Get started by creating your first recurring task to build better habits.
              </p>
              <button
                onClick={handleNewTask}
                className="inline-flex items-center gap-2 bg-[#D97757] hover:bg-[#C4684A] text-white font-medium py-2.5 px-5 rounded-xl shadow-sm"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create your first task
              </button>
            </div>
          )}
        </div>
      </main>

      {user && (
        <>
          <NewTaskModal
            isOpen={showNewTaskModal}
            onClose={() => setShowNewTaskModal(false)}
            onTaskCreated={handleTaskCreated}
            userId={user.id}
          />
          <EditTaskModal
            isOpen={showEditTaskModal}
            onClose={() => setShowEditTaskModal(false)}
            onTaskUpdated={handleTaskUpdated}
            taskId={editingTaskId}
            currentTitle={editingTaskTitle}
          />
        </>
      )}
    </div>
  );
}
