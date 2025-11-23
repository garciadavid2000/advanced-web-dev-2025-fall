'use client';

interface SidebarProps {
  userName: string;
  onNewTask: () => void;
}

export default function Sidebar({ userName, onNewTask }: SidebarProps) {
  return (
    <aside className="w-64 bg-red-600 text-white p-6 flex flex-col h-screen">
      <div className="mb-8">
        <h2 className="text-2xl font-bold">{userName}</h2>
      </div>

      <button
        onClick={onNewTask}
        className="w-full bg-red-700 hover:bg-red-800 text-white font-bold py-3 px-4 rounded border-2 border-red-500 transition duration-200"
      >
        New Task
      </button>

      <div className="flex-1 mt-8">
      </div>
    </aside>
  );
}
