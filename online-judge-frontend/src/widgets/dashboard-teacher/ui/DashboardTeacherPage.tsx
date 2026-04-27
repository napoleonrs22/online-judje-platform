"use client";

import { useCallback, useEffect, useState } from "react";
import { Card } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button/Button";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "../../../../i18n/navigation";
import { AuthError, fetchCurrentUser } from "@/shared/api/auth";
import { canSeeTeacherNav, getPostLoginPath } from "@/shared/lib/role-home";
import {
  fetchTeacherProblems,
  fetchTeacherStudents,
  TeacherApiError,
  TeacherProblemRow,
  TeacherStudentRow,
  updateTeacherProblem,
} from "@/shared/api/teacher";

export default function DashboardTeacherPage() {
  const t = useTranslations("DashboardTeacher");
  const router = useRouter();
  const [allowed, setAllowed] = useState<boolean | null>(null);
  const [problems, setProblems] = useState<TeacherProblemRow[]>([]);
  const [students, setStudents] = useState<TeacherStudentRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [selectedByProblem, setSelectedByProblem] = useState<Record<string, Set<string>>>({});
  const [savingId, setSavingId] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [pRes, studs] = await Promise.all([
        fetchTeacherProblems(),
        fetchTeacherStudents(),
      ]);
      setProblems(pRes.problems);
      setStudents(studs);
      const sel: Record<string, Set<string>> = {};
      for (const p of pRes.problems) {
        sel[p.id] = new Set(p.assigned_student_ids);
      }
      setSelectedByProblem(sel);
    } catch (e) {
      if (e instanceof TeacherApiError) {
        setError(e.message);
      } else {
        setError(t("loadError"));
      }
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    fetchCurrentUser()
      .then((user) => {
        if (!canSeeTeacherNav(user.role)) {
          router.replace(getPostLoginPath(user.role));
          return;
        }
        setAllowed(true);
      })
      .catch((e) => {
        if (e instanceof AuthError && e.statusCode === 401) {
          router.replace("/login");
        } else {
          router.replace("/login");
        }
      });
  }, [router]);

  useEffect(() => {
    if (!allowed) return;
    loadData();
  }, [allowed, loadData]);

  const toggleStudent = (problemId: string, studentId: string) => {
    setSelectedByProblem((prev) => {
      const next = { ...prev };
      const set = new Set(next[problemId] ?? []);
      if (set.has(studentId)) {
        set.delete(studentId);
      } else {
        set.add(studentId);
      }
      next[problemId] = set;
      return next;
    });
  };

  const saveAssignment = async (problem: TeacherProblemRow) => {
    const ids = Array.from(selectedByProblem[problem.id] ?? []);
    setSavingId(problem.id);
    setError(null);
    try {
      await updateTeacherProblem(problem.id, {
        is_public: false,
        assigned_student_ids: ids,
      });
      await loadData();
      setExpandedId(null);
    } catch (e) {
      if (e instanceof TeacherApiError) {
        setError(e.message);
      } else {
        setError(t("saveError"));
      }
    } finally {
      setSavingId(null);
    }
  };

  const publishForAll = async (problem: TeacherProblemRow) => {
    setSavingId(problem.id);
    setError(null);
    try {
      await updateTeacherProblem(problem.id, { is_public: true });
      await loadData();
    } catch (e) {
      if (e instanceof TeacherApiError) {
        setError(e.message);
      } else {
        setError(t("saveError"));
      }
    } finally {
      setSavingId(null);
    }
  };

  if (!allowed) {
    return <p className="text-sm text-slate-500">{t("loading")}</p>;
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            {t("title")}
          </h2>
          <p className="mt-1 text-slate-500">{t("subtitle")}</p>
          <p className="mt-2 text-sm text-slate-500">{t("assignHint")}</p>
        </div>
        <Link href="/problems/create">
          <Button size="sm">{t("createProblem")}</Button>
        </Link>
      </div>

      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      <Card className="p-4">
        <h3 className="mb-3 text-lg font-semibold text-slate-900 dark:text-white">
          {t("myProblems")}
        </h3>
        {loading ? (
          <p className="text-sm text-slate-500">{t("loadingList")}</p>
        ) : problems.length === 0 ? (
          <p className="text-sm text-slate-500">{t("noProblems")}</p>
        ) : (
          <ul className="space-y-3">
            {problems.map((p) => (
              <li
                key={p.id}
                className="rounded-lg border border-slate-200 p-4 dark:border-slate-700"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">{p.title}</p>
                    <p className="text-xs text-slate-500">
                      {p.slug} · {p.difficulty}
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      {p.is_public ? (
                        <span className="text-emerald-600 dark:text-emerald-400">
                          {t("badgePublic")}
                        </span>
                      ) : (
                        <span className="text-amber-600 dark:text-amber-400">
                          {t("badgePrivate")}
                          {` · ${(selectedByProblem[p.id]?.size ?? 0)} ${t("assignedCount")}`}
                        </span>
                      )}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      disabled={savingId === p.id}
                      onClick={() => publishForAll(p)}
                    >
                      {t("publishAll")}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() =>
                        setExpandedId((id) => (id === p.id ? null : p.id))
                      }
                    >
                      {expandedId === p.id ? t("collapse") : t("assignStudents")}
                    </Button>
                  </div>
                </div>

                {expandedId === p.id && (
                  <div className="mt-4 border-t border-slate-100 pt-4 dark:border-slate-800">
                    <p className="mb-2 text-sm text-slate-600 dark:text-slate-400">
                      {t("pickStudents")}
                    </p>
                    <div className="max-h-48 space-y-2 overflow-y-auto rounded-md border border-slate-100 p-2 dark:border-slate-800">
                      {students.length === 0 ? (
                        <p className="text-xs text-slate-500">{t("noStudents")}</p>
                      ) : (
                        students.map((s) => (
                          <label
                            key={s.id}
                            className="flex cursor-pointer items-center gap-2 text-sm text-slate-800 dark:text-slate-200"
                          >
                            <input
                              type="checkbox"
                              checked={selectedByProblem[p.id]?.has(s.id) ?? false}
                              onChange={() => toggleStudent(p.id, s.id)}
                            />
                            <span>
                              {s.username} ({s.email})
                            </span>
                          </label>
                        ))
                      )}
                    </div>
                    <div className="mt-3 flex gap-2">
                      <Button
                        type="button"
                        size="sm"
                        disabled={savingId === p.id}
                        onClick={() => saveAssignment(p)}
                      >
                        {savingId === p.id ? t("saving") : t("saveAssignment")}
                      </Button>
                      <p className="self-center text-xs text-slate-500">
                        {t("privateNote")}
                      </p>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
