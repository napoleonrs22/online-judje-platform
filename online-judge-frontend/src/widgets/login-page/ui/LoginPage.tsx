"use client";

import React, { useState } from 'react';
import { Card } from '@/shared/ui/card/Card'; 
import { Button } from '@/shared/ui/button/Button';
import {useForm, SubmitHandler} from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useRouter } from '../../../../i18n/navigation';
import { AuthError, fetchCurrentUser, login } from '@/shared/api/auth';
import { getPostLoginPath } from '@/shared/lib/role-home';

interface LoginProps {
  onLogin?: () => void;
  onRegister?: () => void;
}

const loginSchema = z.object({
  email: z.string().email('Некорректный email'),
  password: z.string().min(6, 'Минимум 6 символов').max(128, 'Слишком длинный пароль'),
});

type LoginSchema = z.infer<typeof loginSchema>;


export const Login: React.FC<LoginProps> = ({ onRegister }) => {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);

  const {register, handleSubmit, formState: {errors, isSubmitting}} = useForm<LoginSchema>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit: SubmitHandler<LoginSchema> = async (data) => {
    setFormError(null);
    try {
      await login({ email: data.email, password: data.password });
      const user = await fetchCurrentUser();
      router.push(getPostLoginPath(user.role));
    } catch (err) {
      if (err instanceof AuthError) {
        setFormError(err.message);
        return;
      }
      setFormError('Ошибка входа');
    }
  };


  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50 dark:bg-slate-950">
      <Card className="w-full max-w-sm p-8 shadow-md">
        <div className="mb-8">
           <div className="w-10 h-10 bg-slate-900 text-white flex items-center justify-center rounded mb-4">
              {/* <Terminal size={24} /> */}
           </div>
           <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Sign In</h2>
           <p className="text-slate-500 mt-2 text-sm">Access your workspace</p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          {formError && (
            <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200">
              {formError}
            </p>
          )}
          {/* Email поле */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium  text-slate-900 dark:text-white mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              placeholder="name@example.com"
              autoFocus
              {...register('email')}  // register('email') подключает поле к react-hook-form
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
            />
            {errors.email && (
              <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>
            )}
          </div>

          {/* Password поле */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-900 dark:text-white mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              placeholder="password"
              {...register('password')}  // register('password') подключает поле к react-hook-form
              className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-slate-500"
            />
            {errors.password && (
              <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>
            )}
          </div>
          
          <Button type="submit" disabled={isSubmitting} className="w-full mt-2">
            {isSubmitting ? 'Загрузка...' : 'Authenticate'}
          </Button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-100 dark:border-slate-800 text-center text-sm text-slate-500">
          Don&apos;t have an account?{' '}
          {onRegister ? (
            <button type="button" onClick={onRegister} className="font-medium text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">
              Create Account
            </button>
          ) : (
            <Link href="/register" className="font-medium text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">
              Create Account
            </Link>
          )}
        </div>
      </Card>
    </div>
  );
};