'use client';

import { useState } from 'react';
import { exportToCalendar } from '@/apis/api';

interface SidebarProps {
  userName: string;
  onNewTask: () => void;
}

export default function Sidebar({ userName, onNewTask }: SidebarProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [exportMessage, setExportMessage] = useState('');

  const handleExportToCalendar = async () => {
    setIsExporting(true);
    setExportStatus('idle');

    try {
      const result = await exportToCalendar();
      setExportStatus('success');
      setExportMessage(`${result.success} tasks exported${result.failed > 0 ? `, ${result.failed} failed` : ''}`);


      setTimeout(() => setExportStatus('idle'), 5000);
    } catch (error) {
      setExportStatus('error');
      setExportMessage(error instanceof Error ? error.message : 'Failed to export tasks');


      setTimeout(() => setExportStatus('idle'), 5000);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <aside className="w-72 bg-gray-900 text-white p-6 flex flex-col h-screen shadow-xl">

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-[#D97757] flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <span className="text-xl font-semibold tracking-tight">Tasks</span>
        </div>


        <div className="px-3 py-2 rounded-lg bg-gray-800/50">
          <p className="text-sm text-gray-400">Welcome back,</p>
          <p className="font-medium text-white truncate">{userName}</p>
        </div>
      </div>


      <button
        onClick={onNewTask}
        className="w-full bg-[#D97757] hover:bg-[#C4684A] text-white font-semibold py-3 px-4 rounded-xl shadow-lg shadow-[#D97757]/20 flex items-center justify-center gap-2 transition-all duration-200"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        New Task
      </button>


      <button
        onClick={handleExportToCalendar}
        disabled={isExporting}
        className={`w-full mt-3 font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all duration-200 ${isExporting
            ? 'bg-gray-700 text-gray-300 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/20'
          }`}
      >
        {isExporting ? (
          <>
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Exporting...
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Export to Calendar
          </>
        )}
      </button>


      {exportStatus !== 'idle' && (
        <div
          className={`mt-3 p-3 rounded-lg text-sm font-medium animate-fade-in ${exportStatus === 'success'
              ? 'bg-green-900/30 text-green-300 border border-green-700/50'
              : 'bg-red-900/30 text-red-300 border border-red-700/50'
            }`}
        >
          {exportMessage}
        </div>
      )}


      <div className="flex-1 mt-8"></div>


      <div className="pt-4 border-t border-gray-800">
        <p className="text-xs text-gray-500 text-center">Stay productive</p>
      </div>
    </aside>
  );
}

