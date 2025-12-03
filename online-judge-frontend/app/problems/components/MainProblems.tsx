"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getToken } from "@/lib/auth";

interface Problem {
  id: string; // Важно: используем ID
  title: string;
  slug: string;
  difficulty: string;
  is_public: boolean;
  created_at: string;
}

export default function MainProblems() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError(null);

    const token = getToken();
    if (!token) {
      setError("Пользователь не авторизован");
      setLoading(false);
      return;
    }

    fetch(`${API_URL}/student/problems?skip=0&limit=50`, {
      method: "GET",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(`Ошибка ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!mounted) return;
        // Проверка формата ответа: массив или объект с полем problems
        const list = Array.isArray(data) ? data : (data.problems || []);
        setProblems(list);
      })
      .catch((err) => {
        if (!mounted) return;
        console.error(err);
        setError(err.message || "Ошибка загрузки");
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [API_URL]);

  const formatDate = (iso: string) =>
    iso ? new Date(iso).toLocaleString("ru-RU", { hour12: false }) : "";

  // Переход по ID
  const handleCardClick = (id: string) => {
    router.push(`/problems/${id}`);
  };

  return (
    <div className="bg-[#e6e6e6] min-h-screen p-5">
      <h2 className="font-semibold text-black text-2xl">Доступные задачи</h2>

      {loading && (
        <div className="mt-6 animate-pulse space-y-2">
          <div className="h-16 bg-white rounded-md p-4" />
          <div className="h-16 bg-white rounded-md p-4" />
        </div>
      )}

      {error && <div className="mt-4 text-red-600">{error}</div>}

      <div className="grid gap-4 mt-4">
        {problems.map((p) => (
          <div
            key={p.id}
            onClick={() => handleCardClick(p.id)} // ID здесь
            className="flex items-center justify-between gap-3 bg-white p-4 rounded-md shadow-md cursor-pointer hover:shadow-lg transition group"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 flex items-center justify-center rounded bg-[#f3f4f6]">
                <Image alt="problem" src="/Frame (11).svg" width={20} height={20} />
              </div>

              <div>
                <h3 className="text-black font-semibold group-hover:text-blue-600 transition-colors">
                  {p.title}
                </h3>
                <div className="text-sm text-gray-500">
                  {p.difficulty} · {p.is_public ? "Публичная" : "Приватная"}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Image src="/Frame (13).svg" alt="tag" width={20} height={20} />
                <span>{p.slug}</span>
              </div>

              <Link
                href={`/problems/${p.id}`} // Ссылка на ID
                onClick={(e) => e.stopPropagation()}
                className="text-sm px-3 py-1 border rounded text-blue-600 hover:bg-blue-50 transition-colors"
              >
                Решить
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}