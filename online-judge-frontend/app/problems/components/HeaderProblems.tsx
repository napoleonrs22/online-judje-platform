import Image from "next/image"

export default function HeaderProblems() {
  return (
    <>
      <header className="w-full bg-[#F2F2F2] px-5 py-4 justify-between flex items-center">
        <div className="flex gap-6 text-center items-center rounded-md">
          <h2 className="text-black text-base font-semibold">CodeContest</h2>

          <label className="relative bg-[#e6e6e6] rounded-md ">

            <input 
              type="text" 
              placeholder="Найдите задачи или соревнования"
              className="w-full pr-10 pl-3 h-8 focus:outline-none focus-visible:ring-2 rounded-md text-black text-lg" />

            <button 
            className="absolute right-0 top-1/2 -translate-y-1/2 h-8 w-8 p-0 flex items-center justify-center
                       border-none bg-transparent focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-300
                       z-10 cursor-pointer">
               <Image 
              width={25}
              height={25}
              alt="search icon"
              src={"/Frame (6).svg"}
            />
            </button>
           
          </label>
        </div>
        <div className="flex gap-4  items-center">
          <Image 
             width={30}
             height={30}
             alt="search icon"
             src={"/Frame (7).svg"}
             className="cursor-pointer"
          />

          <Image 
             width={30}
             height={30}
             alt="search icon"
             src={"/Frame (8).svg"}
             className="cursor-pointer"
          />

          <div className="flex gap-2 items-center">
            <Image 
             width={30}
             height={30}
             alt="search icon"
             src={"/Frame (9).svg"}
             className="cursor-pointer"
            />

          <p className="text-black font-normal">Danila</p>
            <Image 
              width={20}
              height={20}
              alt="search icon"
              src={"/Frame (10).svg"}
              className="cursor-pointer"
            />
          </div>
        </div>
      </header>
    </>
   )
}