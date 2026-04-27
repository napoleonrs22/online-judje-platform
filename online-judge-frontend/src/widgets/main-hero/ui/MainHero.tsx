"use client";

import {useState} from "react";
import {useLocale, useTranslations} from "next-intl";
import {ArrowRight} from "lucide-react";
import {Button} from "@/shared/ui/button/Button";
import {Link, usePathname, useRouter} from "../../../../i18n/navigation";
import {AuthError, fetchCurrentUser, isAuthenticated} from "@/shared/api/auth";
import {getStartCodingPath} from "@/shared/lib/role-home";

export default function MainHero() {
  const t = useTranslations("MainHero");
  const localeT = useTranslations("Locale");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [navPending, setNavPending] = useState<"coding" | "docs" | null>(null);

  const locales = ["en", "ru", "kk"] as const;

  const handleLocaleChange = (nextLocale: "en" | "ru" | "kk") => {
    router.replace(pathname, {locale: nextLocale});
  };

  const goLogin = () => {
    router.push("/login");
  };

  const handleStartCoding = async () => {
    if (!isAuthenticated()) {
      goLogin();
      return;
    }
    setNavPending("coding");
    try {
      const user = await fetchCurrentUser();
      router.push(getStartCodingPath(user.role));
    } catch (e) {
      if (e instanceof AuthError && e.statusCode === 401) {
        goLogin();
      }
    } finally {
      setNavPending(null);
    }
  };

  const handleDocumentation = async () => {
    if (!isAuthenticated()) {
      goLogin();
      return;
    }
    setNavPending("docs");
    try {
      await fetchCurrentUser();
      router.push("/docs");
    } catch (e) {
      if (e instanceof AuthError && e.statusCode === 401) {
        goLogin();
      }
    } finally {
      setNavPending(null);
    }
  };

  return (
    <>
      <div className="flex flex-col min-h-screen bg-[#0F172A] w-full ">

        {/* NAV */}
        <div className="flex flex-row items-center justify-between p-6 border-b border-slate-200 dark:border-slate-800">
          <div>
            <div>{t("brand")}</div>
          </div>
          <div className="flex items-center gap-3 font-medium text-xs ">
            <div className="flex items-center rounded-full border border-slate-700 bg-slate-900/70 p-1 shadow-sm">
              {locales.map((loc) => (
                <button
                  key={loc}
                  type="button"
                  onClick={() => handleLocaleChange(loc)}
                  className={`min-w-10 rounded-full px-3 py-1.5 text-[11px] tracking-wide transition-all ${
                    locale === loc
                      ? "bg-white text-slate-900 shadow"
                      : "text-slate-300 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  {localeT(loc)}
                </button>
              ))}
            </div>
            <Button variant="outline" size="sm"><Link href="/login">{t("login")}</Link></Button>
            <Button variant="primary" size="sm"><Link href="/register">{t("register")}</Link></Button>
          </div>
        </div>

        {/* HERO */}
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-4xl mx-auto space-y-8" >

          <h1 className='text-5xl md:text-7xl font-bold tracking-tight text-slate-900 dark:text-white'>{t("title")}</h1>

          <p className="text-xl text-slate-500 max-w-2xl font-light">{t("subtitle")}</p>

          <div className="flex gap-4 pt-4">
            <Button
              size="lg"
              type="button"
              disabled={navPending !== null}
              onClick={handleStartCoding}
              className="inline-flex items-center gap-2"
            >
              {t("startCoding")} <ArrowRight size={18} />
            </Button>
            <Button
              size="lg"
              variant="outline"
              type="button"
              disabled={navPending !== null}
              onClick={handleDocumentation}
            >
              {t("documentation")}
            </Button>
          </div>
        </div>

        {/* FOOTER */}
        <div className="py-6 text-center text-xs text-slate-400 uppercase tracking-widest">
         © 2026 Online Judge Platform
      </div>
      </div>
    </>
  )
}











// // app/page.tsx
// 'use client';

// import React from 'react';
// import Link from 'next/link';
// import { Terminal, ArrowRight, Code2, Trophy, Users } from 'lucide-react';
// import  {Button} from "@/app/components/ui/Button";

// // Если Button еще не настроен в алиасах, можно заменить на обычные <button> с классами ниже

// export default function MainHero() {
//   return (
//     <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 overflow-hidden relative">

//       {/* Фоновый эффект (Grid Pattern) - делает дизайн "дорогим" */}
//       <div className="absolute inset-0 -z-10 h-full w-full bg-white dark:bg-slate-950 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]">
//         <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-blue-400 opacity-20 blur-[100px]"></div>
//       </div>

//       {/* Топ бар (Header) */}
//       <nav className="sticky top-0 z-50 w-full border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md">
//         <div className="container mx-auto px-6 h-16 flex items-center justify-between">
//           {/* Логотип */}
//           <div className="flex items-center gap-2 font-bold text-xl text-slate-900 dark:text-white">
//             <div className="bg-slate-900 dark:bg-white text-white dark:text-slate-900 p-1 rounded-md">
//               <Terminal size={18} strokeWidth={3} />
//             </div>
//             CodeContest
//           </div>

//           {/* Кнопки навигации */}
//           <div className="flex items-center gap-4">
//             <Link href="/login">
//               <Button variant="secondary" size="sm">
//                 Войти
//               </Button>
//             </Link>
//             <Link href="/register">
//               <Button variant="primary" size="sm">
//                 Регистрация
//               </Button>
//             </Link>
//           </div>
//         </div>
//       </nav>

//       {/* Основной контент (Hero Section) */}
//       <main className="flex-1 flex flex-col items-center justify-center px-4 pt-20 pb-16 text-center max-w-5xl mx-auto space-y-8">

//         {/* Бейдж "Beta" или "New" */}
//         <div className="animate-fade-in-up inline-flex items-center rounded-full border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 py-1 text-sm text-slate-500 dark:text-slate-400 shadow-sm mb-4">
//           <span className="flex h-2 w-2 rounded-full bg-blue-500 mr-2 animate-pulse"></span>
//           Сезон 2026 открыт
//         </div>

//         {/* Заголовок */}
//         <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-slate-900 dark:text-white leading-[1.1]">
//           Платформа для <br />
//           <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
//             профессионального роста
//           </span>
//         </h1>

//         {/* Подзаголовок */}
//         <p className="text-xl text-slate-500 dark:text-slate-400 max-w-2xl font-light leading-relaxed">
//           Решай алгоритмические задачи, соревнуйся с другими разработчиками и готовься к техническим собеседованиям в IT-гиганты.
//         </p>

//         {/* Кнопки действия */}
//         <div className="flex flex-col sm:flex-row gap-4 pt-4 w-full sm:w-auto">
//           <Link href="/problems" className="w-full sm:w-auto">
//             <Button size="lg" className="w-full sm:w-auto group text-base px-8 h-12">
//               Начать решать
//               <ArrowRight size={18} className="ml-2 group-hover:translate-x-1 transition-transform" />
//             </Button>
//           </Link>
//           <Link href="/leaderboard" className="w-full sm:w-auto">
//              <Button variant="outline" size="lg" className="w-full sm:w-auto h-12 text-base">
//                Таблица лидеров
//              </Button>
//           </Link>
//         </div>

//         {/* Статистика / Преимущества (Features) */}
//         <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-20 w-full border-t border-slate-200 dark:border-slate-800 pt-10">
//            <div className="flex flex-col items-center space-y-2">
//               <div className="p-3 bg-blue-50 dark:bg-slate-800 rounded-full text-blue-600 dark:text-blue-400">
//                  <Code2 size={24} />
//               </div>
//               <h3 className="font-semibold text-slate-900 dark:text-white">500+ Задач</h3>
//               <p className="text-sm text-slate-500">От Easy до Hard уровня</p>
//            </div>
//            <div className="flex flex-col items-center space-y-2">
//               <div className="p-3 bg-purple-50 dark:bg-slate-800 rounded-full text-purple-600 dark:text-purple-400">
//                  <Users size={24} />
//               </div>
//               <h3 className="font-semibold text-slate-900 dark:text-white">Сообщество</h3>
//               <p className="text-sm text-slate-500">Обсуждай решения</p>
//            </div>
//            <div className="flex flex-col items-center space-y-2">
//               <div className="p-3 bg-amber-50 dark:bg-slate-800 rounded-full text-amber-600 dark:text-amber-400">
//                  <Trophy size={24} />
//               </div>
//               <h3 className="font-semibold text-slate-900 dark:text-white">Рейтинг</h3>
//               <p className="text-sm text-slate-500">Стань лучшим в топе</p>
//            </div>
//         </div>
//       </main>

//       {/* Footer (упрощенный) */}
//       <footer className="py-6 text-center text-xs text-slate-400">
//          © 2024 CodeContest Platform. Все права защищены.
//       </footer>
//     </div>
//   );
// }

