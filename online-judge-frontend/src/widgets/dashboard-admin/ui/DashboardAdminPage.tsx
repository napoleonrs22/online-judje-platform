"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Card } from "@/shared/ui/card";
import { Link } from "../../../../i18n/navigation";
import { AuthError, CurrentUser, fetchCurrentUser } from "@/shared/api/auth";
import { useRouter } from "../../../../i18n/navigation";
import { canSeeAdminNav, getPostLoginPath } from "@/shared/lib/role-home";

export default function DashboardAdminPage() {
  const t = useTranslations("DashboardAdmin");
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCurrentUser()
      .then((u) => {
        if (!canSeeAdminNav(u.role)) {
          router.replace(getPostLoginPath(u.role));
          return;
        }
        setUser(u);
      })
      .catch((e) => {
        if (e instanceof AuthError) {
          if (e.statusCode === 401) {
            router.replace("/login");
            return;
          }
          setError(e.message);
        } else {
          setError("Failed to load profile");
        }
      });
  }, [router]);

  if (error) {
    return (
      <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
    );
  }

  if (!user) {
    return (
      <p className="text-sm text-slate-500">{t("loading")}</p>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t("title")}</h1>
          <p className="mt-1 text-slate-500">{t("subtitle")}</p>
        </div>
        <Link
          href="/dashboard/admin/users"
          className="text-sm font-medium text-slate-600 underline hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
        >
          {t("manageUsers")}
        </Link>
      </div>

      <Card className="space-y-3 p-6">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{t("yourAccount")}</h2>
        <dl className="grid gap-2 text-sm">
          <div className="flex justify-between gap-4 border-b border-slate-100 py-2 dark:border-slate-800">
            <dt className="text-slate-500">{t("fullName")}</dt>
            <dd className="font-medium text-slate-900 dark:text-white">{user.full_name}</dd>
          </div>
          <div className="flex justify-between gap-4 border-b border-slate-100 py-2 dark:border-slate-800">
            <dt className="text-slate-500">{t("email")}</dt>
            <dd className="font-medium text-slate-900 dark:text-white">{user.email}</dd>
          </div>
          <div className="flex justify-between gap-4 border-b border-slate-100 py-2 dark:border-slate-800">
            <dt className="text-slate-500">{t("username")}</dt>
            <dd className="font-medium text-slate-900 dark:text-white">{user.username}</dd>
          </div>
          <div className="flex justify-between gap-4 py-2">
            <dt className="text-slate-500">{t("role")}</dt>
            <dd className="font-medium capitalize text-slate-900 dark:text-white">{user.role}</dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
