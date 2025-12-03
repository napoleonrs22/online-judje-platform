
"use client"
import Image from "next/image"
import { useState } from "react"

const MENU = [
  { title: "Панель студента", items: ["Главная", "Мои предметы", "Домашние задания", "Прогресс"] },
  { title: "Настройки", items: ["Профиль", "Уведомления", "Приватность"] }
]

export default function SideMenu() {
  const [openIndex, setOpenIndex] = useState<number>(-1)

  function toggleIndex(i: number) {
    setOpenIndex(prev => (prev === i ? -1 : i))
  }

  return (
    <div className="fixed top-0 left-0 h-full w-64 md:w-56 lg:w-64 bg-[#F2F2F2] shadow-lg border-l-4 border-[#d9d9d9] p-3">
      <div className="flex items-center gap-2 mb-4 p-2">
        <Image width={20} height={20} alt="menu" src="/menu-outline.svg" />
        <h2 className="font-normal text-base text-[#4d4d4d]">Меню</h2>
      </div>

      <nav className="flex flex-col gap-2">
        {MENU.map((block, i) => {
          const isOpen = openIndex === i

          return (
            <div key={i} className="flex flex-col">
              <button
                onClick={() => toggleIndex(i)}
                className="flex justify-between items-center rounded-md py-2 px-2 hover:bg-white transition-colors duration-150"
                aria-expanded={isOpen}
              >
                <div className="flex items-center gap-3">
                  <Image width={20} height={20} alt="icon" src="/user.svg" />
                  <span className="text-black">{block.title}</span>
                </div>

                <div className={`transition-transform duration-300 ${isOpen ? "rotate-90" : "rotate-0"}`}>
                  <Image width={20} height={20} alt="arrow" src="/Frame (10).svg" />
                </div>
              </button>

              {/* Плавное раскрытие через max-h */}
              <div className={`overflow-hidden transition-all duration-300 ${isOpen ? "max-h-40 mt-2" : "max-h-0"}`}>
                {/* Внутренний контейнер — для translateY + opacity */}
                <div className={`ml-10 flex flex-col gap-2 transform transition-all duration-300 ${isOpen ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0"}`}>
                  {block.items.map((it, idx) => (
                    <a key={idx} className="text-sm text-[#4d4d4d] cursor-pointer hover:underline">
                      {it}
                    </a>
                  ))}
                </div>
              </div>
            </div>
          )
        })}
      </nav>
    </div>
  )
}

// НЕ УДАЛЯТЬ!!!
// НЕ УДАЛЯТЬ!!!
// НЕ УДАЛЯТЬ!!!
// НЕ УДАЛЯТЬ!!!
// НЕ УДАЛЯТЬ!!!


// "use client"
// import Image from "next/image"
// import { useState } from "react"

// export default function SideMenu() {

//   const [open, setOpen] = useState(false)

//   function toggleMenu() {
//     setOpen(!open)
//   }
//   return (
//     <>
//       <div className=" fixed top-0 left-0 
//         h-full 
//         w-64          
//         md:w-56      
//         lg:w-64      
//         bg-[#F2F2F2] shadow-lg
//         border-l-4 border-[#d9d9d9] border-solid">
//         <div className="flex mb-4 p-2 gap-2 items-center cursor-pointer">
//           <Image 
//               width={20}
//               height={20}
//               alt="user icon"
//               src={"/menu-outline.svg"}
//             />
//           <h2 className="font-normal text-base text-[#4d4d4d]">Закрыть меню</h2>
//         </div>


//         <div className="flex flex-col p-2 gap-2">


//           <div 
//             className="flex justify-between items-center rounded-md cursor-pointer"
//             onClick={toggleMenu}>


//             <div className="flex gap-3">
//               <Image 
//               width={20}
//               height={20}
//               alt="user icon"
//               src={"/user.svg"}
//               />

//              <span className="text-black cursor-pointer">Панель студента</span>
//             </div>
//               <Image 
//               width={16}
//               height={16}
//               alt="user icon"
//               src={"/Frame (10).svg"}/>
//           </div>


//           {open && (
//             <div className="flex flex-col text-black">
//               <span>Доступные задачи</span>
//               <span>Мой отправки</span>
//               <span>Олимпиады</span>
//             </div>
//           )}


//           <div className="flex justify-between items-center rounded-md cursor-pointer">
//             <div className="flex gap-3">
//               <Image 
//               width={20}
//               height={20}
//               alt="user icon"
//               src={"/user.svg"}
//               />

//              <span className="text-black cursor-pointer font-normal text-base">Панель студента</span>
//             </div>
            
            
//               <Image 
//               width={16}
//               height={16}
//               alt="user icon"
//               src={"/Frame (10).svg"}/>
//           </div>
            
//         </div>
//       </div>
//     </>
//    )


// }