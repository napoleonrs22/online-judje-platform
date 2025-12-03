import { getToken } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface SubmissionPayload {
  problem_id: string;
  language: string;
  code: string;
}

export interface SubmissionResponse {
  submission_id: string;
  user_id: string;
  problem_id: string;
  status: string;       // "ACCEPTED", "WRONG_ANSWER", "COMPILE_ERROR", etc.
  message: string;      // "Вердикт: ACCEPTED"
  final_status: string;
  execution_time: number;
  memory_used: number;
  created_at: string;
}

export async function submitSolution(data: SubmissionPayload): Promise<SubmissionResponse> {
  const token = getToken();

  if (!token) {
    throw new Error("Вы не авторизованы");
  }

  const response = await fetch(`${API_URL}/student/submissions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Ошибка отправки: ${response.status}`);
  }

  return await response.json();
}