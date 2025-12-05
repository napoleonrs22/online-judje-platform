'use client';

import React, { useState, useEffect } from 'react';
import { Settings, ChevronDown, Send } from 'lucide-react';
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
      python: `# Решите задачу "${problem.title}"\n\ndef ${fnName}():\n    # Напишите ваш код здесь\n    pass\n`,
      javascript: `/**\n * ${problem.title}\n */\nfunction ${fnName}() {\n    // Ваш код здесь\n}\n`,
      java: `public class Solution {\n    public static void main(String[] args) {\n        // Ваш код здесь\n    }\n}`,
      cpp: `#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // Ваш код здесь\n    return 0;\n}`
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
      setError(err.message || 'Ошибка при отправке решения');
      setActiveTab('submissions');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="h-[calc(100vh-64px)] w-full flex flex-col bg-gray-50 select-none"
      onMouseMove={handleMouseMove}
      onMouseUp={() => setIsDragging(false)}
      onMouseLeave={() => setIsDragging(false)}
    >
      <div id="split-container" className="flex-1 flex overflow-hidden">

        {/* ЛЕВАЯ ПАНЕЛЬ — Описание */}
        <div style={{ width: `${splitRatio}%` }} className="bg-white flex flex-col border-r border-gray-200">
          <div className="flex bg-gray-50 border-b border-gray-200">
            <button
              onClick={() => setActiveTab('description')}
              className={`px-6 py-3 text-sm font-medium transition-colors border-b-2 ${
                activeTab === 'description'
                  ? 'border-blue-600 text-blue-600 bg-white'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Описание
            </button>
            <button
              onClick={() => setActiveTab('submissions')}
              className={`px-6 py-3 text-sm font-medium transition-colors border-b-2 ${
                activeTab === 'submissions'
                  ? 'border-blue-600 text-blue-600 bg-white'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Мои решения
            </button>
          </div>
          <div className="flex-1 overflow-y-auto bg-white">
            {activeTab === 'description' && <ProblemDescription problem={problem} />}
            {activeTab === 'submissions' && <SubmissionStatus submission={submission} error={error} />}
          </div>
        </div>

        {/* Разделитель */}
        <div
          className="w-1 bg-gray-300 hover:bg-blue-500 cursor-col-resize transition-colors z-10"
          onMouseDown={() => setIsDragging(true)}
        />

        {/* ПРАВАЯ ПАНЕЛЬ — Светлый редактор */}
        <div style={{ width: `${100 - splitRatio}%` }} className="bg-white flex flex-col">

          {/* Header редактора — светлый */}
          <div className="h-12 border-b border-gray-200 flex items-center justify-between px-4 bg-gray-50">
            <div className="flex items-center gap-3">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as any)}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
              </select>
            </div>

            <button className="p-2 hover:bg-gray-200 rounded transition">
              <Settings className="w-5 h-5 text-gray-600" />
            </button>
          </div>

          {/* Редактор — СВЕТЛАЯ ТЕМА */}
          <div className="flex-1 bg-white">
            <CodeEditorWithMirror
              code={code}
              onChange={setCode}
              language={language}
              theme="light"  // ← ВАЖНО: передаём светлую тему
            />
          </div>

          {/* Футер с кнопкой */}
          <div className="h-16 border-t border-gray-200 bg-gray-50 px-6 flex items-center justify-end">
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="px-8 py-3 rounded-lg bg-blue-900 text-white font-semibold text-sm hover:bg-blue-800 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm"
            >
              {isLoading ? (
                <>Отправка...</>
              ) : (
                <>
                  Отправить решение
                  <Send className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}