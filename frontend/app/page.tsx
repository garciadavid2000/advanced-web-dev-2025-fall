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

        // If UnauthorizedError, redirect to sign-in
        if (err instanceof Error && err.name === 'UnauthorizedError') {
          router.push('/signin');
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
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">↻</div>
          <p className="text-lg text-gray-600">Loading your tasks...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-lg text-red-600 mb-4">
            {error || 'Failed to load user data'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Main page layout
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar userName={user.name} onNewTask={handleNewTask} />

      <main className="flex-1 overflow-auto">
        <div className="p-8">
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
            <div className="text-center py-12">
              <p className="text-lg text-gray-600">No tasks scheduled</p>
              <p className="text-sm text-gray-500 mt-2">
                Create a new task to get started
              </p>
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
