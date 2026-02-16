import React from 'react';
import { twMerge } from 'tailwind-merge';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  noPadding?: boolean;
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  className = '', 
  onClick,
  noPadding = false
}) => {
  return (
    <div
      onClick={onClick}
      className={twMerge(
        `bg-white dark:bg-slate-900 
         border border-slate-200 dark:border-slate-800 
         rounded-lg shadow-sm 
         transition-all duration-200`,
        onClick && 'cursor-pointer hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-md',
        !noPadding && 'p-6',
        className
      )}
    >
      {children}
    </div>
  );
};