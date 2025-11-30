// app/login/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { login, AuthError } from '@/lib/auth';

import styles from './Login.module.css';

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
    <div className={styles.auth}>
      {/* ЛЕВАЯ ЧАСТЬ — ФОРМА */}
      <div className={styles.auth_left}>
        <form onSubmit={handleSubmit} className={styles.login_form}>
          {/* Основной контейнер */}


          {/* Заголовок */}
          <div className={styles.login_form__title}>
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

          <div className={styles.form_input}>

          {/* Введите логин - Label */}
          <div className={styles.form_input__label}>
            Введите электронную почту
          </div>
          {/* Введите логин - Input */}
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={styles.form_input__input}
            disabled={isLoading}
            required
          />

          </div>

          <div className={styles.form_input}>
          {/* Введите пароль - Label */}
          <div className={styles.form_input__label}>
            Введите пароль
          </div>
          {/* Введите пароль - Input */}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={styles.form_input__input}
            disabled={isLoading}
            required
          />
          </div>

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
      <div className={styles.auth_right}>
        <Image
          src="/login.png"
          alt="Программист за ноутбуком"
          fill
          className={styles.auth_right_img}
          priority
        />
      </div>
    </div>
  );
}