'use client';

import { useEffect, useState, use } from "react";
import SideMenu from "@/app/problems/components/SideMenu";
import HeaderProblems from "@/app/problems/components/HeaderProblems";
import ProblemSolver from "@/app/problems/components/ProblemSolver";
import { getToken } from "@/lib/auth";

// Интерфейсы
interface ApiProblem {
  id: string;
  title: string;
  slug: string;
  difficulty: string;
  description?: string; // API может не вернуть, если поле называется иначе
  // В ответе API (из вашего curl) нет поля description на верхнем уровне, проверьте бэкенд!
  // Если description нет, возможно, нужно добавить его в схему ответа на бэкенде.
  examples: Array<{ input_data: string; output_data: string; explanation?: string }>;
  test_cases: Array<{ input_data: string; output_data: string }>;
  constraints?: string[];
  topics?: string[];
  time_limit?: number;
  memory_limit?: number;
  acceptance?: string;
}

interface SolverProblem {
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

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function ProblemPage({ params }: PageProps) {
  const { id } = use(params);

  const [problem, setProblem] = useState<SolverProblem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchProblem = async () => {
      setLoading(true);
      setError(null);

      const token = getToken();
      if (!token) {
        setError("Нужна авторизация");
        setLoading(false);
        return;
      }

      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
        const response = await fetch(`${API_URL}/student/problems/${id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json',
          }
        });

        if (!response.ok) {
           throw new Error(`Ошибка: ${response.status}`);
        }

        const data: ApiProblem = await response.json();

        // Маппинг данных из API в UI
        const mappedProblem: SolverProblem = {
          id: data.id,
          title: data.title,
          slug: data.slug,
          // Если description не пришел с бэкенда, ставим заглушку
          description: data.description || "Описание задачи загружается...",
          difficulty: data.difficulty,
          examples: data.examples?.map(ex => ({
            input: ex.input_data,
            output: ex.output_data,
            explanation: ex.explanation || ""
          })) || [],
          constraints: data.constraints || ["Ограничений нет"],
          topics: data.topics || [],
          acceptance: data.acceptance || "N/A",
          time_limit: data.time_limit || 1000,
          memory_limit: data.memory_limit || 256
        };

        setProblem(mappedProblem);
      } catch (err: any) {
        console.error(err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProblem();
  }, [id]);

  if (loading) return (
     <div className="flex h-screen bg-white">
        <SideMenu />
        <div className="flex-1 flex flex-col ml-64 min-w-0">
           <HeaderProblems />
           <div className="flex-1 flex items-center justify-center text-xl text-gray-500">Загрузка...</div>
        </div>
     </div>
  );

  if (error || !problem) return (
     <div className="flex h-screen bg-white">
        <SideMenu />
        <div className="flex-1 flex flex-col ml-64 min-w-0">
           <HeaderProblems />
           <div className="flex-1 flex items-center justify-center text-red-500 font-bold">{error || "Задача не найдена"}</div>
        </div>
     </div>
  );

  return (
    <div className="flex h-screen overflow-hidden bg-white">
      <SideMenu />
      <div className="flex-1 flex flex-col ml-64 min-w-0">
         <HeaderProblems />
         <div className="flex-1 relative">
            <ProblemSolver problem={problem} />
         </div>
      </div>
    </div>
  );
}