'use client';

interface SidebarProps {
  userName: string;
  onNewTask: () => void;
}

export default function Sidebar({ userName, onNewTask }: SidebarProps) {
  return (
    <aside className="w-72 bg-gray-900 text-white p-6 flex flex-col h-screen shadow-xl">
      {/* Logo/Brand */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-[#D97757] flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <span className="text-xl font-semibold tracking-tight">Tasks</span>
        </div>

        {/* User greeting */}
        <div className="px-3 py-2 rounded-lg bg-gray-800/50">
          <p className="text-sm text-gray-400">Welcome back,</p>
          <p className="font-medium text-white truncate">{userName}</p>
        </div>
      </div>

      {/* New Task Button */}
      <button
        onClick={onNewTask}
        className="w-full bg-[#D97757] hover:bg-[#C4684A] text-white font-semibold py-3 px-4 rounded-xl shadow-lg shadow-[#D97757]/20 flex items-center justify-center gap-2"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        New Task
      </button>

      {/* Spacer */}
      <div className="flex-1 mt-8"></div>

      {/* Footer */}
      <div className="pt-4 border-t border-gray-800">
        <p className="text-xs text-gray-500 text-center">Stay productive</p>
      </div>
    </aside>
  );
}
