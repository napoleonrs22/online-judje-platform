"use client";

import { useEffect, useState } from "react";
import { CheckCircle, Clock, TrendingUp } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { formatDistanceToNow } from "date-fns";
import type { Locale } from "date-fns";
import { enUS, ru } from "date-fns/locale";
import { Card } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
import { Link } from "../../../../i18n/navigation";
import {
  DashboardApiError,
  DashboardMeStats,
  fetchDashboardMeStats,
} from "@/shared/api/dashboard";

const dateLocales: Record<string, Locale> = {
  en: enUS,
  ru,
  kk: enUS,
};

function useDateLocale(): Locale {
  const loc = useLocale();
  return dateLocales[loc] ?? enUS;
}

export default function DashboardOverviewPage() {
  const t = useTranslations("DashboardOverview");
  const tStatus = useTranslations("SubmissionStatus");
  const dateLocale = useDateLocale();
  const [stats, setStats] = useState<DashboardMeStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardMeStats()
      .then(setStats)
      .catch((e) => {
        if (e instanceof DashboardApiError) {
          setError(e.message);
        } else {
          setError(t("loadError"));
        }
      });
  }, [t]);

  const statCards = stats
    ? [
        {
          label: t("statSolved"),
          value: String(stats.solved_count),
          icon: CheckCircle,
        },
        {
          label: t("statRank"),
          value: stats.rank != null ? `#${stats.rank}` : "—",
          icon: TrendingUp,
        },
        {
          label: t("statWeekActivity"),
          value: t("statWeekActivityValue", {
            submissions: stats.submissions_this_week,
            hours: stats.estimated_hours_this_week,
          }),
          icon: Clock,
        },
      ]
    : [];

  const formatStatus = (status: string) => {
    const keys = [
      "ACCEPTED",
      "WRONG_ANSWER",
      "PENDING",
      "TIME_LIMIT",
      "RUNTIME_ERROR",
      "COMPILE_ERROR",
      "INTERNAL_ERROR",
      "IN_PROGRESS",
    ] as const;
    if (keys.includes(status as (typeof keys)[number])) {
      return tStatus(status as (typeof keys)[number]);
    }
    return status;
  };

  return (
    <div className="space-y-8">
      <Card className="border-slate-800 bg-gradient-to-r from-slate-950 to-slate-800 text-white">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-2xl font-bold">{t("overview")}</h2>
            <p className="mt-1 text-slate-300">
              {t("welcome")}
            </p>
            {stats && (
              <p className="mt-2 text-sm text-slate-400">
                {t("ratingLine", { rating: stats.rating })}
              </p>
            )}
          </div>
          <Link href="/dashboard/challenges">
            <Button size="sm" className="bg-white text-slate-900 hover:bg-slate-100">
              {t("openChallenges")}
            </Button>
          </Link>
        </div>
      </Card>

      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
          {t("performance")}
        </h2>
        <p className="mt-1 text-slate-500">{t("activityWeek")}</p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {!stats ? (
          <p className="text-sm text-slate-500 md:col-span-3">{t("loadingStats")}</p>
        ) : (
          statCards.map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <Card key={idx} className="flex items-center gap-4 shadow-sm">
                <div className="rounded-md bg-slate-900 p-3 text-white dark:bg-white dark:text-slate-900">
                  <Icon size={20} />
                </div>
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    {stat.label}
                  </p>
                  <p className="text-xl font-bold text-slate-900 dark:text-white">
                    {stat.value}
                  </p>
                </div>
              </Card>
            );
          })
        )}
      </div>

      <Card className="space-y-3">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
          {t("recentActivity")}
        </h3>
        {!stats ? (
          <p className="text-sm text-slate-500">{t("loadingStats")}</p>
        ) : stats.recent_activity.length === 0 ? (
          <p className="text-sm text-slate-500">{t("noActivity")}</p>
        ) : (
          <div className="space-y-2">
            {stats.recent_activity.map((item) => (
              <div
                key={`${item.problem_id}-${item.created_at}`}
                className="flex items-center justify-between rounded-md border border-slate-200 px-3 py-2 dark:border-slate-700"
              >
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-white">
                    {item.problem_title}
                  </p>
                  <p className="text-xs text-slate-500">
                    {item.created_at
                      ? formatDistanceToNow(new Date(item.created_at), {
                          addSuffix: true,
                          locale: dateLocale,
                        })
                      : ""}
                  </p>
                </div>
                <span className="text-xs text-slate-600 dark:text-slate-300">
                  {formatStatus(item.status)}
                </span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
