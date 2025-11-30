// app/page.tsx
'use client';

import Image from 'next/image';
import Link from 'next/link';

export default function MainHero() {
  return (
    <div className="w-full min-h-screen relative overflow-hidden">
      {/* Фоновое изображение */}
      <Image
        src="/main.jpg"
        alt="Code background"
        fill
        className="object-cover -z-10 blur-sm"
        priority
      />

      {/* Топ бар */}
      <nav className="w-full h-14 bg-zinc-100 shadow-[0px_1px_2px_0px_rgba(0,0,0,0.25)] sticky top-0 z-50">
        <div className="w-full h-full px-6 flex justify-between items-center">
          {/* Логотип */}
          <div className="text-black text-2xl font-semibold">
            CodeContest
          </div>

          {/* Кнопки */}
          <div className="flex items-center gap-3">
            {/* Войти */}
            <Link
              href="/login"
              className="px-5 py-2.5 rounded-lg outline outline-2 outline-offset-[-2px] outline-slate-700 inline-flex justify-center items-center gap-2.5 hover:bg-zinc-200 transition text-zinc-950 text-base font-semibold"
            >
              Войти
            </Link>

            {/* Регистрация */}
            <Link
              href="/register"
              className="px-5 py-2.5 bg-indigo-800 rounded-lg inline-flex justify-center items-center gap-2.5 hover:bg-indigo-900 transition text-neutral-200 text-base font-semibold"
            >
              Регистрация
            </Link>
          </div>
        </div>
      </nav>

      {/* Основной контент */}
      <div className="w-full h-[calc(100vh-56px)] flex flex-col items-center justify-center relative z-10 px-4">
        {/* Главный заголовок */}
        <h1 className="text-center text-zinc-100 text-6xl font-semibold leading-tight mb-6">
          Платформа<br />для программистов
        </h1>

        {/* Подзаголовок */}
        <p className="text-center text-zinc-400 text-2xl font-semibold mb-12">
          Решай задачи, развивайся, побеждай!
        </p>

        {/* Кнопка Начать */}
        <button className="w-44 h-10 px-5 py-2.5 bg-sky-900 rounded-lg inline-flex justify-center items-center gap-2.5 hover:bg-sky-950 transition shadow-[0px_2px_4px_0px_rgba(0,0,0,0.25)] text-zinc-100 text-base font-semibold">
          <Link href="/problems">
            Начать
          </Link>
        </button>
      </div>
    </div>
  );
}