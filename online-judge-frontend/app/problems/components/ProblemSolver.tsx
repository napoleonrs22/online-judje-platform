'use client';

import React, { useState, useEffect } from 'react';
import { Settings, Maximize2, RotateCcw, ChevronDown, Send } from 'lucide-react';
import CodeEditorWithMirror from './CodeEditorWithMirror';
import ProblemDescription from './ProblemDescription';
import SubmissionStatus from './SubmissionStatus';
import { submitSolution, SubmissionResponse } from '@/lib/api/submissions';

interface Problem {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  examples: Array<{ input: string; output: string; explanation?: string }>;
  constraints: string[];
  topics: string[];
  acceptance: string;
  time_limit?: number;
  memory_limit?: number;
  slug?: string;
}

export default function ProblemSolver({ problem }: { problem: Problem }) {
  const [splitRatio, setSplitRatio] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const [activeTab, setActiveTab] = useState<'description' | 'submissions'>('description');
  const [language, setLanguage] = useState<'python' | 'cpp' | 'java' | 'javascript'>('python');
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [submission, setSubmission] = useState<SubmissionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Шаблоны кода
  useEffect(() => {
    const fnName = problem.slug ? problem.slug.replace(/-/g, '_') : 'solve';
    const templates: Record<string, string> = {
      python: `def ${fnName}(nums, target):\n    # Write your code here\n    pass`,
      javascript: `/**\n * @param {number[]} nums\n * @param {number} target\n * @return {number[]}\n */\nvar ${fnName} = function(nums, target) {\n    \n};`,
      java: `class Solution {\n    public int[] ${fnName}(int[] nums, int target) {\n        \n    }\n}`,
      cpp: `class Solution {\npublic:\n    vector<int> ${fnName}(vector<int>& nums, int target) {\n        \n    }\n};`
    };
    setCode(templates[language] || '');
  }, [language, problem.slug]);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    const container = document.getElementById('split-container');
    if (container) {
      const rect = container.getBoundingClientRect();
      const newRatio = ((e.clientX - rect.left) / rect.width) * 100;
      if (newRatio > 25 && newRatio < 75) setSplitRatio(newRatio);
    }
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    setSubmission(null);
    try {
      const result = await submitSolution({
        problem_id: problem.id,
        language,
        code,
      });
      setSubmission(result);
      setActiveTab('submissions');
    } catch (err: any) {
      setError(err.message || 'Ошибка сервера');
      setActiveTab('submissions');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="h-[calc(100vh-64px)] w-full flex flex-col bg-gray-100 select-none"
      onMouseMove={handleMouseMove}
      onMouseUp={() => setIsDragging(false)}
      onMouseLeave={() => setIsDragging(false)}
    >
      <div id="split-container" className="flex-1 flex overflow-hidden">

        {/* ЛЕВАЯ ПАНЕЛЬ (СВЕТЛАЯ) */}
        <div style={{ width: `${splitRatio}%` }} className="bg-[#FDFDFD] flex flex-col border-r border-gray-200">
          <div className="flex bg-[#F2F2F2] border-b border-[#E0E0E0]">
            <button
              onClick={() => setActiveTab('description')}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === 'description' ? 'bg-[#FDFDFD] border-t-2 border-t-blue-500 text-black' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Описание
            </button>
            <button
              onClick={() => setActiveTab('submissions')}
              className={`px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === 'submissions' ? 'bg-[#FDFDFD] border-t-2 border-t-blue-500 text-black' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Решения
            </button>
          </div>
          <div className="flex-1 overflow-hidden relative">
            {activeTab === 'description' && <ProblemDescription problem={problem} />}
            {activeTab === 'submissions' && <SubmissionStatus submission={submission} error={error} />}
          </div>
        </div>

        {/* РАЗДЕЛИТЕЛЬ */}
        <div
          className="w-1 bg-gray-300 hover:bg-blue-500 cursor-col-resize z-20 transition-colors"
          onMouseDown={() => setIsDragging(true)}
        />

        {/* ПРАВАЯ ПАНЕЛЬ (ТЕМНАЯ) */}
        <div style={{ width: `${100 - splitRatio}%` }} className="bg-[#1e1e1e] flex flex-col text-white">

          {/* Header редактора */}
          <div className="h-10 border-b border-[#333] flex items-center justify-between px-3 bg-[#F2F2F2]">
            <div className="relative group">
               <div className="bg-white border border-gray-300 rounded px-2 py-1 flex items-center gap-1 cursor-pointer hover:bg-gray-50">
                 <select
                   value={language}
                   onChange={(e) => setLanguage(e.target.value as any)}
                   className="appearance-none bg-transparent text-black text-sm font-medium focus:outline-none cursor-pointer pr-4"
                 >
                   <option value="python">Python</option>
                   <option value="javascript">JavaScript</option>
                   <option value="java">Java</option>
                   <option value="cpp">C++</option>
                 </select>
                 <ChevronDown className="w-3 h-3 text-black pointer-events-none absolute right-2"/>
               </div>
            </div>
            <div className="flex items-center gap-3 text-gray-500">
               <Settings className="w-4 h-4 cursor-pointer hover:text-black" />
            </div>
          </div>

          {/* CodeMirror Редактор */}
          <div className="flex-1 overflow-hidden relative bg-[#1e1e1e]">
            <CodeEditorWithMirror
              code={code}
              onChange={setCode}
              language={language}
            />
          </div>

          {/* Footer (Кнопка отправки) */}
          <div className="h-16 border-t border-[#333] bg-[#F2F2F2] px-4 flex items-center justify-end gap-3">
             <button
               onClick={handleSubmit}
               disabled={isLoading}
               className="px-6 py-2 rounded-md bg-[#0033A0] text-white text-sm font-semibold hover:bg-[#002270] transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
             >
               {isLoading ? 'Отправка...' : 'Отправить решение'}
               {!isLoading && <Send className="w-4 h-4" />}
             </button>
          </div>

        </div>
      </div>
    </div>
  );
}