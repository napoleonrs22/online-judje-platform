"use client";

import { useEffect, useState } from "react";
import { Header } from "@/shared/ui/header";
import { Sidebar } from "@/shared/ui/sidebar";
import { useRouter } from "../../../i18n/navigation";
import { AuthError, CurrentUser, fetchCurrentUser, getToken, logout } from "@/shared/api/auth";
import { DashboardMeStats, fetchDashboardMeStats } from "@/shared/api/dashboard";

function formatRoleLabel(role: string) {
  const r = role.toLowerCase();
  return r.charAt(0).toUpperCase() + r.slice(1);
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [me, setMe] = useState<CurrentUser | null>(null);
  const [dashStats, setDashStats] = useState<DashboardMeStats | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    fetchCurrentUser()
      .then(setMe)
      .catch((e) => {
        if (e instanceof AuthError && e.statusCode === 401) {
          logout();
        }
        router.replace("/login");
      });
  }, [router]);

  useEffect(() => {
    if (!me) return;
    fetchDashboardMeStats()
      .then(setDashStats)
      .catch(() => setDashStats(null));
  }, [me]);

  const handleCloseMobile = () => {
    setIsMobileOpen(false);
  };

  const handleToggleMobile = () => {
    setIsMobileOpen(prev => !prev);
  };

  const handleToggleTheme = () => {
    setIsDark(prev => !prev);
  };

  const handleLogout = () => {
    logout();
    router.replace("/");
  };

  const headerUser = me
    ? {
        id: me.id,
        name: me.full_name || me.username,
        avatar: "/user.svg",
        role: formatRoleLabel(me.role),
        rank: dashStats?.rank ?? 0,
        solved: dashStats?.solved_count ?? 0,
      }
    : {
        id: "",
        name: "…",
        avatar: "/user.svg",
        role: "…",
        rank: 0,
        solved: 0,
      };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <Sidebar 
        isMobileOpen={isMobileOpen}
        closeMobile={handleCloseMobile}
        onLogout={handleLogout}
        userRole={me?.role ?? null}
      />
      <div className="lg:ml-64">
        <Header 
          user={headerUser}
          toggleTheme={handleToggleTheme}
          isDark={isDark}
          toggleMobileSidebar={handleToggleMobile}
        />
        <main className="flex-1 px-8 py-8">
          <div className="mx-auto max-w-6xl">
             {children}
          </div>
        </main>
      </div>
    </div>
  );
}