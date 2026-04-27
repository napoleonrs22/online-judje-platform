"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "../../../../i18n/navigation";
import { fetchCurrentUser, getToken, isAuthenticated } from "@/shared/api/auth";

export default function DocsPage() {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated() || !getToken()) {
      router.replace("/login");
      return;
    }
    fetchCurrentUser().catch(() => {
      router.replace("/login");
    });
  }, [router]);

  return (
    <main className="min-h-screen bg-slate-950 p-6 text-slate-100 md:p-10">
      <div className="mx-auto max-w-3xl space-y-6">
        <h1 className="text-3xl font-bold">Documentation</h1>
        <p className="text-slate-300">
          This section contains quick links for working with the Online Judge
          platform.
        </p>

        <ul className="list-disc space-y-2 pl-5 text-slate-300">
          <li>
            <Link className="underline hover:text-white" href="/problems">
              Problems
            </Link>
          </li>
          <li>
            <Link className="underline hover:text-white" href="/dashboard">
              Dashboard
            </Link>
          </li>
          <li>
            <Link
              className="underline hover:text-white"
              href="http://localhost:8000/docs"
            >
              Backend API Docs
            </Link>
          </li>
        </ul>
      </div>
    </main>
  );
}
