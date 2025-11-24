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
 * Format date string (YYYY-MM-DD) to readable format (Mon Nov 24)
 */
function formatDate(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00');
  const options: Intl.DateTimeFormatOptions = {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  };
  return date.toLocaleDateString('en-US', options);
}

export default function TaskDateGroup({
  date,
  tasks,
  allTasks,
  onCompleteTask,
  onEditTask,
  loadingTaskId,
}: TaskDateGroupProps) {
  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold text-blue-600 mb-4">{formatDate(date)}</h2>

      <div className="space-y-3">
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
