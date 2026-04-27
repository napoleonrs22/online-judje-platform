import React, { useMemo } from 'react';
import { LayoutDashboard, Code2, Trophy, GraduationCap, LogOut, Shield, UserCog } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Link, usePathname } from '../../../../i18n/navigation';
// import { View } from '../types';
import { twMerge } from 'tailwind-merge';
import { canSeeAdminNav, canSeeTeacherNav } from '@/shared/lib/role-home';

interface SidebarProps {
  isMobileOpen: boolean;
  closeMobile: () => void;
  onLogout: () => void;
  userRole: string | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ isMobileOpen, closeMobile, onLogout, userRole }) => {
  const pathname = usePathname();
  const t = useTranslations('Sidebar');

  const menuItems = useMemo(() => {
    const items: {
      href: string;
      label: string;
      icon: typeof LayoutDashboard;
      matchExact?: boolean;
    }[] = [
      { href: '/dashboard', label: t('dashboard'), icon: LayoutDashboard, matchExact: true },
      { href: '/dashboard/challenges', label: t('challenges'), icon: Code2 },
      { href: '/dashboard/leaderboard', label: t('leaderboard'), icon: Trophy },
    ];
    if (userRole && canSeeTeacherNav(userRole)) {
      items.push({ href: '/dashboard/teacher', label: t('teacher'), icon: GraduationCap });
    }
    if (userRole && canSeeAdminNav(userRole)) {
      items.push({ href: '/dashboard/admin', label: t('admin'), icon: Shield, matchExact: true });
      items.push({ href: '/dashboard/admin/users', label: t('userRights'), icon: UserCog });
    }
    return items;
  }, [t, userRole]);

  return (
    <>
      {isMobileOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={closeMobile}
        />
      )}
      
      <aside className={twMerge(
        `fixed top-0 left-0 z-50 h-screen w-64
         bg-white dark:bg-slate-900 
         border-r border-slate-200 dark:border-slate-800
         transition-transform duration-300 ease-out`,
        isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      )}>
        <div className="flex flex-col h-full p-4">
          <div className="flex items-center gap-3 mb-8 px-2 py-2">
            <div className="w-8 h-8 rounded bg-slate-900 text-white flex items-center justify-center">
              <Code2 size={20} />
            </div>
            <h1 className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">
              CodeOlimp
            </h1>
          </div>

          <nav className="space-y-1 flex-1">
            {menuItems.map((item) => {
              const isActive = item.matchExact
                ? pathname === item.href
                : pathname === item.href || pathname.startsWith(`${item.href}/`);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={closeMobile}
                  className={`
                    w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium
                    transition-colors
                    ${isActive 
                      ? 'bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-white' 
                      : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white'
                    }
                  `}
                >
                  <Icon size={18} />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="pt-4 border-t border-slate-200 dark:border-slate-800">
             <button 
                onClick={onLogout}
                className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-slate-500 hover:bg-red-50 hover:text-red-600 transition-colors"
             >
                <LogOut size={18} />
                {t('signOut')}
             </button>
          </div>
        </div>
      </aside>
    </>
  );
};