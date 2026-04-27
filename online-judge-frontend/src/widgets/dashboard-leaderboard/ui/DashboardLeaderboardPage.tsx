"use client";

import { useEffect, useState } from "react";
import { Card } from "@/shared/ui/card";
import { useTranslations } from "next-intl";
import {
  DashboardApiError,
  fetchTopStudents,
  TopStudentRow,
} from "@/shared/api/dashboard";
import { CurrentUser, fetchCurrentUser } from "@/shared/api/auth";

export default function DashboardLeaderboardPage() {
  const t = useTranslations("DashboardLeaderboard");
  const [rows, setRows] = useState<TopStudentRow[]>([]);
  const [me, setMe] = useState<CurrentUser | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    Promise.all([fetchTopStudents(50), fetchCurrentUser().catch(() => null)])
      .then(([list, user]) => {
        if (!cancelled) {
          setRows(list);
          setMe(user);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          if (e instanceof DashboardApiError) {
            setError(e.message);
          } else {
            setError(t("loadError"));
          }
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [t]);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
          {t("title")}
        </h2>
        <p className="mt-1 text-slate-500">
          {t("subtitle")}
        </p>
      </div>

      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      <Card className="space-y-2">
        {loading ? (
          <p className="p-4 text-sm text-slate-500">{t("loading")}</p>
        ) : rows.length === 0 ? (
          <p className="p-4 text-sm text-slate-500">{t("empty")}</p>
        ) : (
          rows.map((user, index) => {
            const isYou = me && user.id === me.id;
            const label = user.full_name || user.username;
            return (
              <div
                key={user.id}
                className={`flex items-center justify-between rounded-md border px-3 py-2 transition-colors dark:border-slate-700 ${
                  isYou
                    ? "border-indigo-300 bg-indigo-50 dark:border-indigo-800 dark:bg-indigo-950/40"
                    : "border-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800/70"
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-slate-900 text-xs font-semibold text-white dark:bg-white dark:text-slate-900">
                    {index + 1}
                  </span>
                  <p className="text-sm font-medium text-slate-900 dark:text-white">
                    {label}
                    {isYou ? ` (${t("you")})` : ""}
                  </p>
                </div>
                <p className="text-xs text-slate-500">
                  {user.solved_count} {t("solved")} | {user.rating} {t("rating")}
                </p>
              </div>
            );
          })
        )}
      </Card>
    </div>
  );
}
