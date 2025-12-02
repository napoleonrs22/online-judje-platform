import HeaderProbems from "./components/HeaderProblems"
import MainProblems from "./components/MainProblems"
import SideMenu from "./components/SideMenu"


// bg-[#E6E6E6]


export default function ProblemsPage() { 
  return (
    <>
    <div >

   
      <SideMenu />
      <div className="flex flex-col ml-64">

    
       <HeaderProbems />
      <MainProblems /> 
        </div>
       </div>
    </>
   )
}