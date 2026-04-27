import React from 'react';
import { Bell, Menu, Moon, Search, Sun } from 'lucide-react';
// import { User } from '../types';

export interface User {
  id: string;
  name: string;
  avatar: string;
  role: string;
  rank: number;
  solved: number;
}


interface HeaderProps {
  user: User;
  toggleTheme: () => void;
  isDark: boolean;
  toggleMobileSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ user, toggleTheme, isDark, toggleMobileSidebar }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
      <div className="px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button 
            onClick={toggleMobileSidebar}
            className="lg:hidden p-2 -ml-2 rounded-md hover:bg-slate-100 text-slate-500"
          >
            <Menu size={20} />
          </button>
          
          <div className="relative hidden sm:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
            <input 
              type="text" 
              placeholder="Search..." 
              className="
                pl-9 pr-4 py-1.5 w-64
                bg-slate-100 dark:bg-slate-800 
                border-transparent focus:border-slate-300 dark:focus:border-slate-600
                rounded-md text-sm
                outline-none
                transition-all
                focus:ring-0
              "
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button className="relative text-slate-500 hover:text-slate-700 transition-colors">
            <Bell size={20} />
            <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-slate-900" />
          </button>

          <button 
            onClick={toggleTheme}
            className="text-slate-500 hover:text-slate-700 transition-colors"
          >
            {isDark ? <Sun size={20} /> : <Moon size={20} />}
          </button>

          <div className="w-px h-6 bg-slate-200 dark:bg-slate-700 mx-2" />

          <div className="flex items-center gap-3">
            <div className="text-right hidden md:block">
              <div className="text-sm font-medium text-slate-900 dark:text-white leading-tight">
                {user.name}
              </div>
              <div className="text-xs text-slate-500">
                {user.role}
              </div>
            </div>
            <img 
              src={user.avatar} 
              alt={user.name} 
              className="w-8 h-8 rounded bg-slate-200"
            />
          </div>
        </div>
      </div>
    </header>
  );
};