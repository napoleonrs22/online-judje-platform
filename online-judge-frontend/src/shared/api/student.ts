import { getToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export class StudentApiError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
    this.name = "StudentApiError";
  }
}

async function authFetch(path: string, init?: RequestInit): Promise<Response> {
  const token = getToken();
  if (!token) {
    throw new StudentApiError(401, "Not authenticated");
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

export interface ProblemExample {
  id: string;
  problem_id: string;
  input_data: string;
  output_data: string;
  explanation: string | null;
}

export interface StudentProblemDetail {
  id: string;
  title: string;
  slug: string;
  difficulty: string;
  is_public: boolean;
  user_id: string;
  description: string;
  created_at: string;
  updated_at: string | null;
  examples: ProblemExample[];
}

export async function fetchStudentProblem(problemId: string): Promise<StudentProblemDetail> {
  const res = await authFetch(`/student/problems/${problemId}`);
  if (!res.ok) {
    const t = await res.text();
    throw new StudentApiError(res.status, t);
  }
  return res.json();
}

export type SubmitLanguage = "python" | "java" | "cpp" | "javascript";

export interface SubmissionResult {
  submission_id: string;
  user_id?: string;
  problem_id?: string;
  status: string;
  message: string;
  final_status: string;
  created_at?: string;
  language?: string;
  execution_time?: number;
  memory_used?: number;
}

export async function submitSolution(body: {
  problem_id: string;
  language: SubmitLanguage;
  code: string;
}): Promise<SubmissionResult> {
  const res = await authFetch("/student/submissions", {
    method: "POST",
    body: JSON.stringify({
      problem_id: body.problem_id,
      language: body.language,
      code: body.code,
    }),
  });
  if (!res.ok) {
    const t = await res.text();
    throw new StudentApiError(res.status, t);
  }
  return res.json();
}
