'use client';

import { TaskOccurrence } from '@/lib/api';

interface TaskCardProps {
  task: TaskOccurrence;
  isCompleteDisabled: boolean;
  onComplete: () => void;
  onEdit: (taskId: number, currentTitle: string) => void;
  isLoading?: boolean;
}

export default function TaskCard({
  task,
  isCompleteDisabled,
  onComplete,
  onEdit,
  isLoading = false,
}: TaskCardProps) {
  const handleClick = () => {
    if (!isCompleteDisabled && !isLoading) {
      onComplete();
    }
  };

  return (
    <div className="border-2 border-blue-500 rounded p-4 mb-3 flex items-center justify-between bg-white hover:bg-gray-50">
      <div
        className="flex-1 cursor-pointer hover:text-blue-600 transition"
        onClick={() => onEdit(task.task_id, task.title)}
      >
        <h3 className="text-lg text-gray-800 font-medium">{task.title}</h3>
        <p className="text-sm text-gray-500">Streak: {task.streak}</p>
      </div>

      <button
        onClick={handleClick}
        disabled={isCompleteDisabled || isLoading}
        className={`ml-4 w-12 h-12 border-2 rounded transition duration-200 ${
          isCompleteDisabled || isLoading
            ? 'border-gray-300 bg-gray-200 cursor-not-allowed'
            : 'border-blue-500 bg-white hover:bg-blue-50 cursor-pointer'
        }`}
        title={isCompleteDisabled ? 'Can only complete the next upcoming task' : 'Mark as complete'}
        aria-label={`Complete ${task.title}`}
      >
        {isLoading ? (
          <span className="flex items-center justify-center h-full">
            <span className="animate-spin">↻</span>
          </span>
        ) : (
          <span className="text-xl">{isCompleteDisabled ? '' : '✓'}</span>
        )}
      </button>
    </div>
  );
}
