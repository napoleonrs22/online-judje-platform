"use client";

import { useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import {
  AvailableProblem,
  DashboardApiError,
  fetchAvailableProblems,
} from "@/shared/api/dashboard";
import {
  fetchStudentProblem,
  StudentApiError,
  StudentProblemDetail,
  submitSolution,
  SubmitLanguage,
} from "@/shared/api/student";

const DIFFICULTY_CLASS: Record<string, string> = {
  Легкий: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200",
  Средний: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200",
  Сложный: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200",
};

const CODE_STUBS: Record<SubmitLanguage, string> = {
  python: `def solve():
    # read input, print answer
    pass
`,
  cpp: `#include <iostream>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    return 0;
}
`,
  java: `import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
    }
}
`,
  javascript: `function main() {
  const readline = require("readline");
}
`,
};

export default function DashboardChallengesPage() {
  const t = useTranslations("DashboardChallenges");
  const [problems, setProblems] = useState<AvailableProblem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<StudentProblemDetail | null>(null);
  const [language, setLanguage] = useState<SubmitLanguage>("python");
  const [code, setCode] = useState(CODE_STUBS.python);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingProblem, setLoadingProblem] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [resultMsg, setResultMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refreshProblemList = async () => {
    try {
      const list = await fetchAvailableProblems({ limit: 100 });
      setProblems(list);
      setSelectedId((prev) => {
        if (prev && list.some((p) => p.id === prev)) return prev;
        return list[0]?.id ?? null;
      });
    } catch {
      /* ignore refresh errors after submit */
    }
  };

  useEffect(() => {
    let cancelled = false;
    setLoadingList(true);
    setError(null);
    fetchAvailableProblems({ limit: 100 })
      .then((list) => {
        if (cancelled) return;
        setProblems(list);
        setSelectedId((prev) => {
          if (prev && list.some((p) => p.id === prev)) return prev;
          return list[0]?.id ?? null;
        });
      })
      .catch((e) => {
        if (cancelled) return;
        if (e instanceof DashboardApiError) {
          setError(e.message);
        } else {
          setError(t("loadError"));
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingList(false);
      });
    return () => {
      cancelled = true;
    };
  }, [t]);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }
    let cancelled = false;
    setLoadingProblem(true);
    setResultMsg(null);
    fetchStudentProblem(selectedId)
      .then((d) => {
        if (!cancelled) setDetail(d);
      })
      .catch((e) => {
        if (!cancelled) {
          if (e instanceof StudentApiError) {
            setError(e.message);
          } else {
            setError(t("loadError"));
          }
          setDetail(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoadingProblem(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedId, t]);

  useEffect(() => {
    setCode(CODE_STUBS[language] || CODE_STUBS.python);
  }, [language]);

  const difficultyBadgeClass = useMemo(() => {
    if (!detail) return DIFFICULTY_CLASS["Легкий"];
    return DIFFICULTY_CLASS[detail.difficulty] || "bg-slate-100 text-slate-700";
  }, [detail]);

  const difficultyLabel = useMemo(() => {
    if (!detail) return "";
    const m: Record<string, string> = {
      Легкий: t("easy"),
      Средний: t("medium"),
      Сложный: t("hard"),
    };
    return m[detail.difficulty] || detail.difficulty;
  }, [detail, t]);

  const handleSubmit = async () => {
    if (!detail || !code || code.length < 10) {
      setResultMsg(t("codeTooShort"));
      return;
    }
    setSubmitting(true);
    setResultMsg(null);
    try {
      const res = await submitSolution({
        problem_id: detail.id,
        language,
        code,
      });
      setResultMsg(
        `${t("verdict")}: ${res.final_status} — ${res.message || ""}`.trim()
      );
      await refreshProblemList();
    } catch (e) {
      if (e instanceof StudentApiError) {
        setResultMsg(e.message);
      } else {
        setResultMsg(t("submitError"));
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{t("title")}</h2>
        <p className="mt-1 text-slate-500">{t("subtitle")}</p>
      </div>

      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <Card className="xl:col-span-3 overflow-hidden p-0">
          <div className="border-b border-slate-200 px-4 py-3 dark:border-slate-800">
            <p className="text-sm font-semibold text-slate-900 dark:text-white">{t("problemSet")}</p>
          </div>
          <div className="max-h-[560px] overflow-y-auto">
            {loadingList ? (
              <p className="px-4 py-6 text-sm text-slate-500">{t("loadingProblems")}</p>
            ) : problems.length === 0 ? (
              <p className="px-4 py-6 text-sm text-slate-500">{t("noProblems")}</p>
            ) : (
              problems.map((problem, index) => (
                <button
                  key={problem.id}
                  type="button"
                  onClick={() => setSelectedId(problem.id)}
                  className={`w-full border-b border-slate-100 px-4 py-3 text-left transition-colors dark:border-slate-800 ${
                    selectedId === problem.id
                      ? "bg-slate-100 dark:bg-slate-800"
                      : "hover:bg-slate-50 dark:hover:bg-slate-800/60"
                  }`}
                >
                  <p className="text-sm font-medium text-slate-900 dark:text-white">
                    {index + 1}. {problem.title}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {problem.difficulty} | {t("acceptance")} {problem.success_rate}%
                  </p>
                </button>
              ))
            )}
          </div>
        </Card>

        <Card className="xl:col-span-4 space-y-4">
          {loadingProblem ? (
            <p className="text-sm text-slate-500">{t("loadingProblem")}</p>
          ) : !detail ? (
            <p className="text-sm text-slate-500">{t("selectProblem")}</p>
          ) : (
            <>
              <div className="flex items-center justify-between gap-2">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                  {detail.title}
                </h3>
                <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${difficultyBadgeClass}`}>
                  {difficultyLabel}
                </span>
              </div>

              <p className="whitespace-pre-wrap text-sm leading-6 text-slate-600 dark:text-slate-300">
                {detail.description}
              </p>

              {detail.examples?.length > 0 && (
                <div className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm dark:border-slate-700 dark:bg-slate-800/60">
                  <p className="font-medium text-slate-900 dark:text-white">{t("example1")}</p>
                  <p className="mt-1 text-slate-600 dark:text-slate-300">
                    {t("input")}: {detail.examples[0].input_data}
                  </p>
                  <p className="text-slate-600 dark:text-slate-300">
                    {t("output")}: {detail.examples[0].output_data}
                  </p>
                  {detail.examples[0].explanation && (
                    <p className="mt-1 text-slate-600 dark:text-slate-300">
                      {detail.examples[0].explanation}
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </Card>

        <Card className="xl:col-span-5 overflow-hidden p-0">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 px-4 py-3 dark:border-slate-800">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm font-medium text-slate-900 dark:text-white">
                {t("editor")}
              </span>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as SubmitLanguage)}
                className="rounded border border-slate-200 bg-white px-2 py-1 text-xs dark:border-slate-700 dark:bg-slate-900"
              >
                <option value="python">Python</option>
                <option value="cpp">C++</option>
                <option value="java">Java</option>
                <option value="javascript">JavaScript</option>
              </select>
            </div>
            <Button size="sm" disabled={submitting || !detail} onClick={handleSubmit}>
              {submitting ? t("submitting") : t("submit")}
            </Button>
          </div>
          {resultMsg && (
            <div className="border-b border-slate-200 px-4 py-2 text-xs text-slate-700 dark:border-slate-800 dark:text-slate-300">
              {resultMsg}
            </div>
          )}
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            spellCheck={false}
            className="h-[520px] w-full resize-none bg-slate-950 p-4 font-mono text-sm text-slate-100 outline-none"
          />
        </Card>
      </div>
    </div>
  );
}
