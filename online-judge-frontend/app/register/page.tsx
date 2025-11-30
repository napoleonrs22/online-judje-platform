// app/register/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { register, AuthError } from '@/lib/auth';

export default function RegisterPage() {
  const router = useRouter();
  const [role, setRole] = useState<'student' | 'teacher'>('student');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');

    // Валидация
    if (!username.trim()) {
      setError('Введите имя пользователя');
      return;
    }
    if (!email.trim()) {
      setError('Введите email');
      return;
    }
    if (!fullName.trim()) {
      setError('Введите полное имя');
      return;
    }
    if (password.length < 6) {
      setError('Пароль должен быть не менее 6 символов');
      return;
    }
    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    setIsLoading(true);

    try {
      await register({
        username,
        email,
        password,
        full_name: fullName,
        role,
      });

      // Успешная регистрация
      router.push('/login?success=registered');
    } catch (err) {
      if (err instanceof AuthError) {
        setError(err.message);
      } else {
        setError('Произошла ошибка при регистрации');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* ЛЕВАЯ ЧАСТЬ — ФОРМА */}
      <div className="w-full lg:w-1/2 flex items-center justify-center bg-gray-50 px-4 py-12">
        <form onSubmit={handleSubmit} className="w-96 relative">
          {/* Основной контейнер */}
          <div className="w-96 bg-zinc-100 rounded-lg shadow-[0px_2px_4px_0px_rgba(0,0,0,0.25)] p-8">
            {/* Заголовок */}
            <h1 className="text-2xl font-semibold text-stone-950 mb-8">
              Регистрация аккаунта
            </h1>

            {/* Ошибка */}
            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
                {error}
              </div>
            )}

            {/* Форма */}
            <div className="space-y-4">
              {/* Выбор роли */}
              <div>
                <label className="block text-base text-neutral-600 mb-2">
                  Выберите роль
                </label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setRole('student')}
                    className={`flex-1 px-4 py-2 rounded-md text-base font-normal transition ${
                      role === 'student'
                        ? 'bg-white text-black border-2 border-zinc-300'
                        : 'bg-neutral-200 text-black border-2 border-zinc-300'
                    }`}
                  >
                    Студент
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole('teacher')}
                    className={`flex-1 px-4 py-2 rounded-md text-base font-normal transition ${
                      role === 'teacher'
                        ? 'bg-white text-black border-2 border-zinc-300'
                        : 'bg-neutral-200 text-black border-2 border-zinc-300'
                    }`}
                  >
                    Преподаватель
                  </button>
                </div>
              </div>

              {/* Nickname */}
              <div>
                <label className="block text-base text-neutral-600 mb-1">
                  Придумайте имя пользователя
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full h-7 px-2 bg-neutral-200 rounded-lg border-2 border-zinc-300 text-stone-950 focus:outline-none"
                  required
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-base text-neutral-600 mb-1">
                  Введите электронную почту
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full h-7 px-2 bg-neutral-200 rounded-lg border-2 border-zinc-300 text-stone-950 focus:outline-none"
                  required
                />
              </div>

              {/* Полное имя */}
              <div>
                <label className="block text-base text-neutral-600 mb-1">
                  Введите полное имя
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full h-7 px-2 bg-neutral-200 rounded-lg border-2 border-zinc-300 text-stone-950 focus:outline-none"
                  required
                />
              </div>

              {/* Пароль */}
              <div>
                <label className="block text-base text-neutral-600 mb-1">
                  Придумайте пароль
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-7 px-2 bg-neutral-200 rounded-lg border-2 border-zinc-300 text-stone-950 focus:outline-none"
                  required
                />
              </div>

              {/* Подтверждение пароля */}
              <div>
                <label className="block text-base text-neutral-600 mb-1">
                  Повторите пароль
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full h-7 px-2 bg-neutral-200 rounded-lg border-2 border-zinc-300 text-stone-950 focus:outline-none"
                  required
                />
              </div>

              {/* Ссылки */}
              <div className="flex items-center justify-between text-xs text-neutral-600 pt-2">
                <Link href="/forgot-password" className="hover:text-stone-950">
                  Забыли пароль?
                </Link>
                <span>•</span>
                <span>Нет аккаунта?</span>
                <Link href="/login" className="text-indigo-900 hover:text-indigo-950 font-semibold">
                  Зарегистрироваться
                </Link>
              </div>

              {/* Кнопка */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full h-8 mt-2 bg-blue-900 hover:bg-blue-950 disabled:bg-blue-400 text-zinc-100 text-base font-semibold rounded-lg transition-all"
              >
                {isLoading ? 'Загрузка...' : 'Вход'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* ПРАВАЯ ЧАСТЬ — ФОТО */}
      <div className="hidden lg:flex w-1/2 relative bg-gray-900 overflow-hidden">
        <Image
          src="/register.png"
          alt="Код"
          fill
          className="object-cover"
          priority
        />
      </div>
    </div>
  );
}