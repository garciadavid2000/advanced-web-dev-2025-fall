'use client';

import { TaskOccurrence } from '@/apis/api';

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
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md hover:border-gray-200 flex items-center justify-between group">
      <div
        className="flex-1 cursor-pointer"
        onClick={() => onEdit(task.task_id, task.title)}
      >
        <h3 className="text-base font-medium text-gray-900 group-hover:text-[#D97757]">
          {task.title}
        </h3>
        <div className="flex items-center gap-2 mt-1">
          <span className="inline-flex items-center gap-1 text-sm text-gray-500">
            <svg className="w-4 h-4 text-[#D97757]" fill="currentColor" viewBox="0 0 20 20">
              <path d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" />
            </svg>
            {task.streak} day streak
          </span>
        </div>
      </div>

      <button
        onClick={handleClick}
        disabled={isCompleteDisabled || isLoading}
        className={`ml-4 w-11 h-11 rounded-full flex items-center justify-center ${isCompleteDisabled || isLoading
            ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
            : 'bg-[#D97757]/10 text-[#D97757] hover:bg-[#D97757] hover:text-white cursor-pointer'
          }`}
        title={isCompleteDisabled ? 'Can only complete the next upcoming task' : 'Mark as complete'}
        aria-label={`Complete ${task.title}`}
      >
        {isLoading ? (
          <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
          </svg>
        )}
      </button>
    </div>
  );
}
