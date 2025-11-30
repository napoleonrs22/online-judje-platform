// app/login/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { login, AuthError } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  // Проверяем, была ли успешная регистрация
  useEffect(() => {
    if (searchParams.get('success') === 'registered') {
      setSuccess('Регистрация успешна! Введите свои учетные данные');
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Валидация
    if (!email.trim()) {
      setError('Введите email');
      return;
    }
    if (!password.trim()) {
      setError('Введите пароль');
      return;
    }

    setIsLoading(true);

    try {
      await login({
        email,
        password,
      });

      // Успешный вход
      router.push('/problems');
    } catch (err) {
      if (err instanceof AuthError) {
        if (err.statusCode === 422) {
          setError('Неверный логин или пароль');
        } else {
          setError(err.message);
        }
      } else {
        setError('Произошла ошибка при входе');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* ЛЕВАЯ ЧАСТЬ — ФОРМА */}
      <div className="w-full lg:w-1/2 flex items-center justify-center bg-gray-50 px-4 py-12">
        <form onSubmit={handleSubmit} className="w-96 h-72 relative">
          {/* Основной контейнер */}
          <div className="w-96 h-72 absolute inset-0 bg-zinc-100 rounded-lg shadow-[0px_2px_4px_0px_rgba(0,0,0,0.25)]" />

          {/* Заголовок */}
          <div className="absolute left-5 top-4 text-stone-950 text-2xl font-semibold">
            Авторизация в аккаунт
          </div>

          {/* Успешное сообщение */}
          {success && (
            <div className="absolute left-5 top-[48px] right-5 p-2 bg-green-100 border border-green-400 text-green-700 rounded text-xs">
              {success}
            </div>
          )}

          {/* Ошибка */}
          {error && (
            <div className="absolute left-5 top-[48px] right-5 p-2 bg-red-100 border border-red-400 text-red-700 rounded text-xs">
              {error}
            </div>
          )}

          {/* Введите логин - Label */}
          <div className="absolute left-5 top-[65px] text-neutral-600 text-base font-normal">
            Введите электронную почту
          </div>
          {/* Введите логин - Input */}
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-96 h-7 absolute left-5 top-[88px] bg-neutral-200 rounded-lg border-2 border-zinc-300 px-2 focus:outline-none text-stone-950"
            disabled={isLoading}
            required
          />

          {/* Введите пароль - Label */}
          <div className="absolute left-5 top-[138px] text-neutral-600 text-base font-normal">
            Введите пароль
          </div>
          {/* Введите пароль - Input */}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-96 h-7 absolute left-5 top-[161px] bg-neutral-200 rounded-lg border-2 border-zinc-300 px-2 focus:outline-none text-stone-950"
            disabled={isLoading}
            required
          />

          {/* Ссылки */}
          <div className="absolute left-5 top-[199px] text-xs font-normal flex gap-2">
            <Link href="/forgot-password" className="text-neutral-600 hover:underline">
              Забыли пароль?
            </Link>
            <span className="text-neutral-600">•</span>
            <span className="text-neutral-600">Нет аккаунта?</span>
            <Link href="/register" className="text-indigo-900 hover:underline font-semibold">
              Зарегистрироваться
            </Link>
          </div>

          {/* Кнопка Вход */}
          <button
            type="submit"
            disabled={isLoading}
            className="h-7 px-12 py-2.5 absolute left-[128px] top-[230px] bg-blue-900 hover:bg-blue-950 disabled:bg-blue-400 rounded-lg shadow-[0px_2px_4px_0px_rgba(0,0,0,0.25)] inline-flex justify-center items-center text-zinc-100 text-base font-semibold transition-all"
          >
            {isLoading ? 'Загрузка...' : 'Вход'}
          </button>
        </form>
      </div>

      {/* ПРАВАЯ ЧАСТЬ — ФОТО */}
      <div className="hidden lg:flex w-1/2 relative bg-gray-900 overflow-hidden">
        <Image
          src="/login.png"
          alt="Программист за ноутбуком"
          fill
          className="object-cover"
          priority
        />
      </div>
    </div>
  );
}