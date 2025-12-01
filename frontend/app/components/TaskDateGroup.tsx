'use client';

import TaskCard from './TaskCard';
import { TaskOccurrence, TasksByDate, canCompleteTask } from '@/apis/api';

interface TaskDateGroupProps {
  date: string;
  tasks: TaskOccurrence[];
  allTasks: TasksByDate;
  onCompleteTask: (occurrenceId: number, taskId: number) => void;
  onEditTask: (taskId: number, currentTitle: string) => void;
  loadingTaskId?: number;
}

/**
 * Format date string (YYYY-MM-DD) to readable format
 */
function formatDate(dateStr: string): { weekday: string; date: string; isToday: boolean } {
  const date = new Date(dateStr + 'T00:00:00');
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const isToday = date.getTime() === today.getTime();

  const weekday = date.toLocaleDateString('en-US', { weekday: 'long' });
  const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

  return { weekday, date: formattedDate, isToday };
}

export default function TaskDateGroup({
  date,
  tasks,
  allTasks,
  onCompleteTask,
  onEditTask,
  loadingTaskId,
}: TaskDateGroupProps) {
  const { weekday, date: formattedDate, isToday } = formatDate(date);

  return (
    <div className="mb-8">
      {/* Date Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="flex items-center gap-2">
          <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <h2 className="text-lg font-semibold text-gray-900">
            {isToday ? 'Today' : weekday}
          </h2>
          <span className="text-sm text-gray-500">{formattedDate}</span>
        </div>
        {isToday && (
          <span className="px-2 py-0.5 text-xs font-medium bg-[#D97757]/10 text-[#D97757] rounded-full">
            Today
          </span>
        )}
      </div>

      {/* Task Cards */}
      <div className="space-y-3 pl-7">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            isCompleteDisabled={!canCompleteTask(allTasks, task.task_id, date)}
            onComplete={() => onCompleteTask(task.id, task.task_id)}
            onEdit={onEditTask}
            isLoading={loadingTaskId === task.id}
          />
        ))}
      </div>
    </div>
  );
}
