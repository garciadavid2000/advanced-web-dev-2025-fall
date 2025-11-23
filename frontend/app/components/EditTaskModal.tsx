'use client';

import { useState, useEffect } from 'react';
import Modal from './Modal';

interface EditTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTaskUpdated: () => void;
  taskId: number | null;
  currentTitle: string;
  isLoading?: boolean;
}

export default function EditTaskModal({
  isOpen,
  onClose,
  onTaskUpdated,
  taskId,
  currentTitle,
  isLoading = false,
}: EditTaskModalProps) {
  const [title, setTitle] = useState(currentTitle);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Update title when modal opens or currentTitle changes
  useEffect(() => {
    if (isOpen) {
      setTitle(currentTitle);
      setError(null);
    }
  }, [isOpen, currentTitle]);

  const handleSubmit = async () => {
    setError(null);

    // Validation
    if (!title.trim()) {
      setError('Task title is required');
      return;
    }

    if (title.trim() === currentTitle.trim()) {
      setError('Please make a change to update the task');
      return;
    }

    if (!taskId) {
      setError('Task ID not found');
      return;
    }

    try {
      setSubmitting(true);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'}/tasks/${taskId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            title: title.trim(),
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update task');
      }

      onClose();
      onTaskUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error updating task:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!submitting && !deleting) {
      setTitle(currentTitle);
      setError(null);
      onClose();
    }
  };

  const handleDelete = async () => {
    if (!taskId) {
      setError('Task ID not found');
      return;
    }

    if (!confirm('Are you sure you want to delete this task? This cannot be undone.')) {
      return;
    }

    try {
      setDeleting(true);
      setError(null);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'}/tasks/${taskId}`,
        {
          method: 'DELETE',
          credentials: 'include',
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete task');
      }

      onClose();
      onTaskUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error deleting task:', err);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      title="Edit Task"
      onClose={handleClose}
      footer={
        <div className="flex gap-3 justify-between">
          <button
            onClick={handleDelete}
            disabled={deleting || submitting}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
          >
            {deleting ? 'Deleting...' : 'Delete Task'}
          </button>
          <div className="flex gap-3">
            <button
              onClick={handleClose}
              disabled={submitting || deleting}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting || isLoading || deleting || title.trim() === currentTitle.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? 'Updating...' : 'Update Task'}
            </button>
          </div>
        </div>
      }
    >
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Task Title
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Task title"
            disabled={submitting || deleting}
            autoFocus
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50"
          />
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
            {error}
          </div>
        )}
      </div>
    </Modal>
  );
}
