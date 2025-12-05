'use client';

import { CheckCircle, AlertCircle, Clock, Database, Terminal } from 'lucide-react';
import { SubmissionResponse } from '@/lib/api/submissions';

interface Props {
  submission: SubmissionResponse | null;
  error?: string | null;
}

export default function SubmissionStatus({ submission, error }: Props) {
  if (error) {
    return (
      <div className="p-8 text-center flex flex-col items-center justify-center h-full bg-white">
        <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
           <AlertCircle className="w-6 h-6 text-red-600" />
        </div>
        <h3 className="text-lg font-semibold text-red-600 mb-2">Ошибка отправки</h3>
        <p className="text-gray-500 text-sm">{error}</p>
      </div>
    );
  }

  if (!submission) return null;

  const isAccepted = submission.status === 'ACCEPTED';
  const colorClass = isAccepted ? 'text-green-600 bg-green-50 border-green-200' : 'text-red-600 bg-red-50 border-red-200';
  const Icon = isAccepted ? CheckCircle : AlertCircle;

  return (
    <div className="p-6 bg-white h-full overflow-y-auto">
      <div className={`p-6 rounded-xl border ${colorClass} mb-6`}>
        <div className="flex items-center gap-3 mb-2">
          <Icon className="w-6 h-6" />
          <h2 className="text-xl font-bold">{submission.status}</h2>
        </div>
        <p className="opacity-80 ml-9">{submission.message}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
          <div className="flex items-center gap-2 text-gray-500 text-xs uppercase font-bold mb-1">
            <Clock className="w-3 h-3" /> Runtime
          </div>
          <div className="text-xl font-mono text-gray-900">{submission.execution_time} ms</div>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
          <div className="flex items-center gap-2 text-gray-500 text-xs uppercase font-bold mb-1">
            <Database className="w-3 h-3" /> Memory
          </div>
          <div className="text-xl font-mono text-gray-900">{submission.memory_used / 1024} MB</div>
        </div>
      </div>

      <div className="text-xs text-gray-400 flex items-center gap-2 justify-center mt-8">
        <Terminal className="w-3 h-3" />
        Submission ID: {submission.submission_id}
      </div>
    </div>
  );
}