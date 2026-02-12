import { Button } from '@/src/shared/ui/button/Button';
import { ArrowRight } from 'lucide-react';

export default function MainHero() {
  return (
    <>
      <div className="flex flex-col min-h-screen bg-[#0F172A] w-full ">

        {/* NAV */}
        <div className="flex flex-row items-center justify-between p-6 border-b border-slate-200 dark:border-slate-800">
          <div>
            <div>Online Judge Platform</div>
          </div>
          <div className="flex gap-4 font-medium text-xs ">
            <Button variant="outline" size="sm">Log in</Button>
            <Button variant="primary" size="sm">Register</Button>
          </div>
        </div>

        {/* HERO */}
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-4xl mx-auto space-y-8" >

          <h1 className='text-5xl md:text-7xl font-bold tracking-tight text-slate-900 dark:text-white'>Master the code</h1>

          <p className="text-xl text-slate-500 max-w-2xl font-light">A strict, no-distraction environment for developers to solve problems, compete in groups, and improve algorithmic skills.</p>

          <div className="flex gap-4 pt-4">
            <Button size="lg">Start Coding <ArrowRight size={18} /></Button>
            <Button size="lg" variant="outline">Documentation</Button>
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

