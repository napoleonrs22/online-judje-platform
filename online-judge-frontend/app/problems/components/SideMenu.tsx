import Image from "next/image"

export default function SideMenu() {
  return (
    <>
      <div className=" fixed top-0 left-0 
        h-full 
        w-64          
        md:w-56      
        lg:w-64      
        bg-[#F2F2F2] shadow-lg
        border-l-4 border-[#d9d9d9] border-solid">
        <div className="flex mb-4 p-2 gap-2 items-center cursor-pointer">
          <Image 
              width={20}
              height={20}
              alt="user icon"
              src={"/menu-outline.svg"}
            />
          <h2 className="font-normal text-base text-[#4d4d4d]">Закрыть меню</h2>
        </div>
        <div className="flex flex-col p-2 gap-2">
          <div className="flex justify-between items-center rounded-md cursor-pointer">
            <div className="flex gap-3">
              <Image 
              width={20}
              height={20}
              alt="user icon"
              src={"/user.svg"}
              />

             <span className="text-black cursor-pointer">Панель студента</span>
            </div>
            
            
              <Image 
              width={20}
              height={20}
              alt="user icon"
              src={"/Frame (10).svg"}/>
          </div>
          <div className="flex justify-between items-center rounded-md cursor-pointer">
            <div className="flex gap-3">
              <Image 
              width={20}
              height={20}
              alt="user icon"
              src={"/user.svg"}
              />

             <span className="text-black cursor-pointer font-normal text-base">Панель студента</span>
            </div>
            
            
              <Image 
              width={20}
              height={20}
              alt="user icon"
              src={"/Frame (10).svg"}/>
          </div>
            
        </div>
      </div>
    </>
   )


}