import { getToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export class DashboardApiError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
    this.name = "DashboardApiError";
  }
}

async function authFetch(path: string, init?: RequestInit): Promise<Response> {
  const token = getToken();
  if (!token) {
    throw new DashboardApiError(401, "Not authenticated");
  }
  return fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...init?.headers,
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
}

export interface DashboardMeStats {
  rating: number;
  solved_count: number;
  rank: number | null;
  submissions_this_week: number;
  estimated_hours_this_week: number;
  recent_activity: {
    problem_id: string;
    problem_title: string;
    status: string;
    created_at: string | null;
  }[];
}

export async function fetchDashboardMeStats(): Promise<DashboardMeStats> {
  const res = await authFetch("/dashboard/me-stats");
  if (!res.ok) {
    throw new DashboardApiError(res.status, await res.text());
  }
  return res.json();
}

export interface AvailableProblem {
  id: string;
  title: string;
  slug: string;
  difficulty: string;
  is_public: boolean;
  author: string | null;
  success_rate: number;
}

export async function fetchAvailableProblems(params?: {
  skip?: number;
  limit?: number;
}): Promise<AvailableProblem[]> {
  const search = new URLSearchParams();
  search.set("skip", String(params?.skip ?? 0));
  search.set("limit", String(params?.limit ?? 50));
  const res = await authFetch(`/dashboard/available-problems?${search}`);
  if (!res.ok) {
    throw new DashboardApiError(res.status, await res.text());
  }
  return res.json();
}

export interface TopStudentRow {
  id: string;
  username: string;
  full_name: string | null;
  email: string;
  university_id: string | null;
  rating: number;
  solved_count: number;
}

export async function fetchTopStudents(limit = 50): Promise<TopStudentRow[]> {
  const res = await authFetch(`/dashboard/top-students?limit=${limit}`);
  if (!res.ok) {
    throw new DashboardApiError(res.status, await res.text());
  }
  return res.json();
}
