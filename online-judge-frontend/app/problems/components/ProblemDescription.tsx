import React from 'react';

interface Problem {
  title: string;
  description: string;
  difficulty: string;
  examples: Array<{ input: string; output: string; explanation?: string }>;
  constraints: string[];
  topics: string[];
  acceptance?: string;
}

export default function ProblemDescription({ problem }: { problem: Problem }) {
  // Настройка цветов сложности как в Figma
  const getDifficultyStyle = (diff: string) => {
    switch (diff.toLowerCase()) {
      case 'easy':
      case 'легкий':
        return 'bg-[#1D8F09]/10 text-[#1D8F09]'; // Lime-700
      case 'medium':
      case 'средний':
        return 'bg-yellow-700/10 text-yellow-700';
      case 'hard':
      case 'сложный':
        return 'bg-red-700/10 text-red-700';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="p-6 h-full overflow-y-auto bg-white text-black font-sans">
      {/* Заголовок и Сложность */}
      <div className="mb-4">
        <div className="flex items-center gap-4 mb-4">
          <div className={`h-6 px-3 py-1 rounded-lg inline-flex justify-center items-center gap-2.5 ${getDifficultyStyle(problem.difficulty)}`}>
            <div className="text-base font-normal font-['Inter']">{problem.difficulty}</div>
          </div>
          {problem.acceptance && (
            <span className="text-gray-400 text-xs">Acceptance: {problem.acceptance}</span>
          )}
        </div>
        <h1 className="text-3xl font-bold mb-4">{problem.title}</h1>
      </div>

      {/* Описание */}
      <div className="mb-8 text-[#4C4C4C] text-base font-normal font-['Inter'] leading-6">
        <p>{problem.description}</p>
      </div>

      {/* Примеры (Examples) - Стилизация под Figma */}
      {problem.examples.map((ex, idx) => (
        <div key={idx} className="mb-6 relative bg-[#D9D9D9]/30 rounded-lg p-5">
           {/* Декоративный фон если нужен, но bg-[#D9D9D9]/30 дает похожий эффект zinc-300 */}

          <h3 className="text-black text-base font-semibold font-['Inter'] mb-2">Example {idx + 1}:</h3>
          <div className="flex flex-col gap-1">
            <div className="flex gap-2">
               <span className="text-[#006699] font-semibold font-['Inter']">Input:</span>
               <span className="text-[#4C4C4C] font-mono">{ex.input}</span>
            </div>
            <div className="flex gap-2">
               <span className="text-[#006699] font-semibold font-['Inter']">Output:</span>
               <span className="text-[#4C4C4C] font-mono">{ex.output}</span>
            </div>
            {ex.explanation && (
              <div className="flex flex-col mt-1">
                 <span className="text-[#4C4C4C] font-semibold font-['Inter']">Explanation:</span>
                 <span className="text-[#4C4C4C]">{ex.explanation}</span>
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Ограничения (Constraints) */}
      <div className="mb-6">
        <h3 className="text-black text-base font-semibold font-['Inter'] mb-3">Constraints:</h3>
        <ul className="space-y-2">
          {problem.constraints.map((c, i) => (
            <li key={i} className="flex items-start gap-2 text-[#4C4C4C] text-base font-normal font-['Inter']">
               <span className="font-bold">•</span>
               <span className="font-mono bg-gray-100 px-1 rounded">{c}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Темы (Topics) */}
      <div className="mb-8">
        <h3 className="text-black text-base font-semibold font-['Inter'] mb-3">Topics:</h3>
        <div className="flex gap-2 flex-wrap">
          {problem.topics.map((topic) => (
            <div key={topic} className="h-6 px-3 py-1 bg-[#D9D9D9] rounded-lg flex justify-center items-center">
               <span className="text-[#4C4C4C] text-sm font-normal font-['Inter']">{topic}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}