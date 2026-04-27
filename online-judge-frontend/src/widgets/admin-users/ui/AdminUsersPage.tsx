"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "../../../../i18n/navigation";
import { Card } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button/Button";
import { AuthError, CurrentUser, fetchCurrentUser } from "@/shared/api/auth";
import {
  AdminApiError,
  AdminRoleParam,
  AdminUserRow,
  adminChangeUserRole,
  adminListUsers,
} from "@/shared/api/admin";
import { canSeeAdminNav, getPostLoginPath } from "@/shared/lib/role-home";

const ROLE_OPTIONS: { value: AdminRoleParam; key: "student" | "teacher" | "admin" }[] = [
  { value: "STUDENT", key: "student" },
  { value: "TEACHER", key: "teacher" },
  { value: "ADMIN", key: "admin" },
];

function toApiRole(r: string): AdminRoleParam {
  const u = r.toUpperCase();
  if (u === "TEACHER" || u === "ADMIN" || u === "STUDENT") {
    return u as AdminRoleParam;
  }
  return "STUDENT";
}

export default function AdminUsersPage() {
  const t = useTranslations("AdminUsers");
  const router = useRouter();
  const [gateUser, setGateUser] = useState<CurrentUser | null>(null);
  const [gateError, setGateError] = useState<string | null>(null);
  const [rows, setRows] = useState<AdminUserRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);
  const [roleFilter, setRoleFilter] = useState<string>("");
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [localRoles, setLocalRoles] = useState<Record<string, AdminRoleParam>>({});

  const loadUsers = useCallback(async () => {
    setListError(null);
    setLoading(true);
    try {
      const data = await adminListUsers({
        skip: 0,
        limit: 100,
        role: roleFilter || undefined,
      });
      setRows(data);
      const initial: Record<string, AdminRoleParam> = {};
      for (const u of data) {
        initial[u.id] = toApiRole(u.role);
      }
      setLocalRoles(initial);
    } catch (e) {
      if (e instanceof AdminApiError) {
        setListError(e.message);
      } else {
        setListError(t("loadError"));
      }
    } finally {
      setLoading(false);
    }
  }, [roleFilter, t]);

  useEffect(() => {
    fetchCurrentUser()
      .then((u) => {
        if (!canSeeAdminNav(u.role)) {
          router.replace(getPostLoginPath(u.role));
          return;
        }
        setGateUser(u);
      })
      .catch((e) => {
        if (e instanceof AuthError && e.statusCode === 401) {
          router.replace("/login");
          return;
        }
        setGateError(e instanceof Error ? e.message : "Error");
      });
  }, [router]);

  useEffect(() => {
    if (!gateUser) return;
    loadUsers();
  }, [gateUser, loadUsers]);

  const onRoleSelect = (userId: string, value: AdminRoleParam) => {
    setLocalRoles((prev) => ({ ...prev, [userId]: value }));
  };

  const applyRole = async (userId: string) => {
    const newRole = localRoles[userId];
    if (!newRole) return;
    const row = rows.find((r) => r.id === userId);
    if (row && toApiRole(row.role) === newRole) {
      return;
    }
    if (
      gateUser &&
      userId === gateUser.id &&
      newRole !== "ADMIN" &&
      !window.confirm(t("confirmDemoteSelf"))
    ) {
      return;
    }
    setPendingId(userId);
    setListError(null);
    try {
      const updated = await adminChangeUserRole(userId, newRole);
      setRows((prev) => prev.map((r) => (r.id === userId ? { ...r, ...updated } : r)));
    } catch (e) {
      if (e instanceof AdminApiError) {
        setListError(e.message);
      } else {
        setListError(t("updateError"));
      }
    } finally {
      setPendingId(null);
    }
  };

  if (gateError) {
    return <p className="text-sm text-red-600 dark:text-red-400">{gateError}</p>;
  }

  if (!gateUser) {
    return <p className="text-sm text-slate-500">{t("loading")}</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t("title")}</h1>
          <p className="mt-1 text-slate-500">{t("subtitle")}</p>
          <p className="mt-2 text-sm text-slate-500">{t("hint")}</p>
        </div>
        <Link
          href="/dashboard/admin"
          className="text-sm font-medium text-slate-600 underline hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
        >
          {t("backToAdmin")}
        </Link>
      </div>

      <Card className="p-4">
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <label className="text-sm text-slate-600 dark:text-slate-400">
            {t("filterRole")}
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="ml-2 rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm dark:border-slate-600 dark:bg-slate-900"
            >
              <option value="">{t("filterAll")}</option>
              <option value="student">{t("roleStudent")}</option>
              <option value="teacher">{t("roleTeacher")}</option>
              <option value="admin">{t("roleAdmin")}</option>
            </select>
          </label>
          <Button type="button" variant="outline" size="sm" onClick={() => loadUsers()}>
            {t("refresh")}
          </Button>
        </div>

        {listError && (
          <p className="mb-3 text-sm text-red-600 dark:text-red-400">{listError}</p>
        )}

        {loading ? (
          <p className="text-sm text-slate-500">{t("loadingList")}</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700">
                  <th className="pb-2 pr-4 font-semibold text-slate-900 dark:text-white">
                    {t("colEmail")}
                  </th>
                  <th className="pb-2 pr-4 font-semibold text-slate-900 dark:text-white">
                    {t("colUsername")}
                  </th>
                  <th className="pb-2 pr-4 font-semibold text-slate-900 dark:text-white">
                    {t("colName")}
                  </th>
                  <th className="pb-2 pr-4 font-semibold text-slate-900 dark:text-white">
                    {t("colRole")}
                  </th>
                  <th className="pb-2 font-semibold text-slate-900 dark:text-white">
                    {t("colActions")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {rows.map((u) => {
                  const selected = localRoles[u.id] ?? toApiRole(u.role);
                  const unchanged = toApiRole(u.role) === selected;
                  return (
                    <tr
                      key={u.id}
                      className="border-b border-slate-100 dark:border-slate-800"
                    >
                      <td className="py-3 pr-4 text-slate-700 dark:text-slate-300">{u.email}</td>
                      <td className="py-3 pr-4 text-slate-700 dark:text-slate-300">{u.username}</td>
                      <td className="py-3 pr-4 text-slate-700 dark:text-slate-300">
                        {u.full_name ?? "—"}
                      </td>
                      <td className="py-3 pr-4">
                        <select
                          value={selected}
                          onChange={(e) =>
                            onRoleSelect(u.id, e.target.value as AdminRoleParam)
                          }
                          disabled={pendingId === u.id}
                          className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm dark:border-slate-600 dark:bg-slate-900"
                        >
                          {ROLE_OPTIONS.map((opt) => (
                            <option key={opt.value} value={opt.value}>
                              {t(`roleOption.${opt.key}`)}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td className="py-3">
                        <Button
                          type="button"
                          size="sm"
                          variant="secondary"
                          disabled={unchanged || pendingId === u.id}
                          onClick={() => applyRole(u.id)}
                        >
                          {pendingId === u.id ? t("saving") : t("apply")}
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {rows.length === 0 && (
              <p className="py-8 text-center text-sm text-slate-500">{t("empty")}</p>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}
