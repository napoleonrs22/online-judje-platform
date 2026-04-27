import { getToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export class TeacherApiError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
    this.name = "TeacherApiError";
  }
}

async function authFetch(path: string, init?: RequestInit): Promise<Response> {
  const token = getToken();
  if (!token) {
    throw new TeacherApiError(401, "Not authenticated");
  }
  return fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...init?.headers,
      Authorization: `Bearer ${token}`,
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
    },
  });
}

export interface TeacherProblemRow {
  id: string;
  title: string;
  slug: string;
  difficulty: string;
  is_public: boolean;
  assigned_student_ids: string[];
  created_at: string | null;
}

export interface TeacherStudentRow {
  id: string;
  username: string;
  email: string;
  full_name: string;
}

export async function fetchTeacherProblems(): Promise<{
  total: number;
  problems: TeacherProblemRow[];
}> {
  const res = await authFetch("/teacher/problems?limit=100");
  if (!res.ok) {
    throw new TeacherApiError(res.status, await res.text());
  }
  return res.json();
}

export async function fetchTeacherStudents(): Promise<TeacherStudentRow[]> {
  const res = await authFetch("/teacher/students?limit=500");
  if (!res.ok) {
    throw new TeacherApiError(res.status, await res.text());
  }
  return res.json();
}

export async function updateTeacherProblem(
  problemId: string,
  body: {
    is_public?: boolean;
    assigned_student_ids?: string[];
  }
): Promise<void> {
  const res = await authFetch(`/teacher/problems/${problemId}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new TeacherApiError(res.status, await res.text());
  }
}
