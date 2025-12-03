'use client';

// Импорты компонентов из папки components, которая лежит рядом
import MainProblems from "./components/MainProblems";
import HeaderProblems from "./components/HeaderProblems";
import SideMenu from "./components/SideMenu";

export default function ProblemsListPage() {
  return (
    <div className="flex h-screen overflow-hidden bg-white">
      {/* Боковое меню */}
      <SideMenu />

      {/* Основная контентная область */}
      <div className="flex-1 flex flex-col ml-64 min-w-0">
        <HeaderProblems />

        {/* Список задач */}
        <div className="flex-1 overflow-y-auto">
            <MainProblems />
        </div>
      </div>
    </div>
  );
}