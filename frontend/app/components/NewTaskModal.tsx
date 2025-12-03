'use client';

import { useState } from 'react';
import Modal from './Modal';
import { API_BASE_URL } from '../../apis/api';

interface NewTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTaskCreated: () => void;
  userId: number;
  isLoading?: boolean;
}

const DAYS_OF_WEEK = [
  { label: 'Mon', value: 'mon' },
  { label: 'Tue', value: 'tue' },
  { label: 'Wed', value: 'wed' },
  { label: 'Thu', value: 'thu' },
  { label: 'Fri', value: 'fri' },
  { label: 'Sat', value: 'sat' },
  { label: 'Sun', value: 'sun' },
];

const TASK_CATEGORIES = [
  'General',
  'Work',
  'Personal',
  'Health',
  'Finance',
  'Travel',
  'Entertainment',
  'Family',
];

export default function NewTaskModal({
  isOpen,
  onClose,
  onTaskCreated,
  userId,
  isLoading = false,
}: NewTaskModalProps) {
  const [title, setTitle] = useState('');
  const [selectedDays, setSelectedDays] = useState<string[]>([]);
  const [category, setCategory] = useState('General');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleDayToggle = (day: string) => {
    setSelectedDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
    );
  };

  const handleSubmit = async () => {
    setError(null);


    if (!title.trim()) {
      setError('Task title is required');
      return;
    }

    if (selectedDays.length === 0) {
      setError('Please select at least one day');
      return;
    }

    try {
      setSubmitting(true);

      console.log(category)

      const response = await fetch(
        `${API_BASE_URL}/tasks`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            user_id: userId,
            title: title.trim(),
            frequency: selectedDays,
            category: category,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create task');
      }


      setTitle('');
      setSelectedDays([]);
      onClose();
      onTaskCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error creating task:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!submitting) {
      setTitle('');
      setSelectedDays([]);
      setCategory('General');
      setError(null);
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      title="Create New Task"
      onClose={handleClose}
      footer={
        <div className="flex gap-3 justify-end">
          <button
            onClick={handleClose}
            disabled={submitting}
            className="px-5 py-2.5 text-gray-600 font-medium rounded-lg hover:bg-gray-100 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting || isLoading}
            className="px-5 py-2.5 bg-[#D97757] text-white font-medium rounded-lg hover:bg-[#C4684A] disabled:opacity-50 shadow-sm"
          >
            {submitting ? 'Creating...' : 'Create Task'}
          </button>
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
            placeholder="e.g., Go to gym"
            disabled={submitting}
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] focus:bg-white disabled:bg-gray-100 placeholder:text-gray-400"
          />
        </div>


        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Repeat on
          </label>
          <div className="grid grid-cols-7 gap-2">
            {DAYS_OF_WEEK.map((day) => (
              <button
                key={day.value}
                onClick={() => handleDayToggle(day.value)}
                disabled={submitting}
                className={`py-2.5 px-1 rounded-lg font-medium text-sm disabled:opacity-50 ${selectedDays.includes(day.value)
                  ? 'bg-[#D97757] text-white shadow-sm'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
              >
                {day.label}
              </button>
            ))}
          </div>
        </div>


        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            disabled={submitting}
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D97757]/30 focus:border-[#D97757] focus:bg-white disabled:bg-gray-100"
          >
            {TASK_CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
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
