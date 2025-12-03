'use client';

import { useState, useEffect } from 'react';
import Modal from './Modal';
import { API_BASE_URL } from '../../apis/api';

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
        `${API_BASE_URL}/tasks/${taskId}`,
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
        `${API_BASE_URL}/tasks/${taskId}`,
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
        <div className="flex gap-3 justify-between items-center">
          <button
            onClick={handleDelete}
            disabled={deleting || submitting}
            className="px-4 py-2.5 text-red-600 font-medium rounded-lg hover:bg-red-50 disabled:opacity-50 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            {deleting ? 'Deleting...' : 'Delete'}
          </button>
          <div className="flex gap-3">
            <button
              onClick={handleClose}
              disabled={submitting || deleting}
              className="px-5 py-2.5 text-gray-600 font-medium rounded-lg hover:bg-gray-100 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting || isLoading || deleting || title.trim() === currentTitle.trim()}
              className="px-5 py-2.5 bg-[#D97757] text-white font-medium rounded-lg hover:bg-[#C4684A] disabled:opacity-50 shadow-sm"
            >
              {submitting ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      }
    >
      <div className="space-y-5">
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
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] focus:bg-white disabled:bg-gray-100 placeholder:text-gray-400"
          />
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-100 rounded-lg text-red-600 text-sm flex items-center gap-2">
            <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            {error}
          </div>
        )}
      </div>
    </Modal>
  );
}
