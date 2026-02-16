"use client";

import React from 'react';
import { Card } from '@/shared/ui/card/Card'; 
import { Button } from '@/shared/ui/button/Button';
import {useForm, SubmitHandler} from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
// import { Input } from '@/shared/ui/input'; // TODO: создать Input компонент
// import { Terminal } from 'lucide-react';

interface LoginProps {
  onLogin?: () => void;
  onRegister?: () => void;
}

// Схема валидации с правильным синтаксисом zod
const loginSchema = z.object({
  email: z.email('Некорректный email'),  // z.string().email(), а не z.email()
  password: z.string().min(6, 'Минимум 6 символов').max(12, 'Максимум 12 символов')
})

type LoginSchema = z.infer<typeof loginSchema>;


export const Login: React.FC<LoginProps> = ({ onLogin, onRegister }) => {

  // Подключаем zodResolver для автоматической валидации
  const {register, handleSubmit, formState: {errors, isSubmitting}} = useForm<LoginSchema>({
    resolver: zodResolver(loginSchema)  // Это связывает zod схему с react-hook-form
  })

  const onSubmit: SubmitHandler<LoginSchema> = (data) => {
    console.log(data)
  }


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
          Don't have an account?{' '}
          <button onClick={onRegister} className=" font-medium  text-slate-500 hover:cursor-pointer hover:text-white">
            Create Account
          </button>
        </div>
      </Card>
    </div>
  );
};