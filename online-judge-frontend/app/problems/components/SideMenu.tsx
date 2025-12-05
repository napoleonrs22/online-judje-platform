"use client"
import Image from "next/image"
import { useState } from "react"
import { useRouter } from "next/navigation"

// ✅ ТИПИЗИРОВАННОЕ МЕНЮ
interface MenuItem {
  title: string
  icon?: string
  items: Array<{
    label: string
    href?: string
  }>
}

const MENU: MenuItem[] = [
  {
    title: "Панель студента",
    icon: "/user.svg",
    items: [
      { label: "Главная" },
      { label: "Мои предметы" },
      { label: "Домашние задания" },
      { label: "Прогресс" }
    ]
  },
  {
    title: "Настройки",
    icon: "/user.svg",
    items: [
      { label: "Профиль" },
      { label: "Уведомления" },
      { label: "Приватность" }
    ]
  },
  {
    title: "Панель преподователя",
    icon: "/user.svg",
    items: [
      { label: "Доступные задачи" },
      { label: "Создать задачу", href: "/problems/create" }, // ✨ СРАЗУ НА ПОЛНУЮ ФОРМУ
      { label: "Статистика" },
      { label: "Студенты" },
      { label: "Отправки" }
    ]
  }
]

// ✅ ОСНОВНОЙ КОМПОНЕНТ
export default function SideMenu() {
  const [openIndex, setOpenIndex] = useState<number>(-1)
  const router = useRouter()

  function toggleIndex(i: number) {
    setOpenIndex(prev => (prev === i ? -1 : i))
  }

  const handleMenuItemClick = (item: MenuItem['items'][0]) => {
    if (item.href) {
      router.push(item.href)
    }
  }

  return (
    <>
      {/* БОКОВОЕ МЕНЮ */}
      <div className="fixed top-0 left-0 h-full w-64 md:w-56 lg:w-64 bg-[#F2F2F2] shadow-lg border-r-4 border-[#d9d9d9] p-3 z-30 overflow-y-auto">
        <div className="flex items-center gap-2 mb-4 p-2">
          <Image width={20} height={20} alt="menu" src="/menu-outline.svg" />
          <h2 className="font-normal text-base text-[#4d4d4d]">Меню</h2>
        </div>

        <nav className="flex flex-col gap-2">
          {MENU.map((block, i) => {
            const isOpen = openIndex === i

            return (
              <div key={i} className="flex flex-col">
                {/* ЗАГОЛОВОК БЛОКА */}
                <button
                  onClick={() => toggleIndex(i)}
                  className="flex justify-between items-center rounded-md py-2 px-2 hover:bg-white hover:shadow-sm transition-all duration-150"
                  aria-expanded={isOpen}
                >
                  <div className="flex items-center gap-3">
                    <Image width={20} height={20} alt="icon" src={block.icon || "/user.svg"} />
                    <span className="text-black font-medium">{block.title}</span>
                  </div>

                  <div className={`transition-transform duration-300 ${isOpen ? "rotate-90" : "rotate-0"}`}>
                    <Image width={20} height={20} alt="arrow" src="/Frame (10).svg" />
                  </div>
                </button>

                {/* РАСКРЫВАЮЩИЕСЯ ПУНКТЫ */}
                <div className={`overflow-hidden transition-all duration-300 ${isOpen ? "max-h-96 mt-2" : "max-h-0"}`}>
                  <div className={`ml-10 flex flex-col gap-2 transform transition-all duration-300 ${isOpen ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0"}`}>
                    {block.items.map((item, idx) => (
                      <div key={idx}>
                        {/* ✅ С ССЫЛКОЙ */}
                        {item.href ? (
                          <button
                            onClick={() => handleMenuItemClick(item)}
                            className="text-sm text-[#4d4d4d] cursor-pointer hover:underline hover:text-blue-600 transition-colors text-left py-1 w-full"
                          >
                            {item.label}
                          </button>
                        ) : (
                          /* ✅ БЕЗ ССЫЛКИ */
                          <a className="text-sm text-[#4d4d4d] cursor-pointer hover:underline py-1">
                            {item.label}
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )
          })}
        </nav>
      </div>
    </>
  )
}