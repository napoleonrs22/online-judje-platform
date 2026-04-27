import { getToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface AdminUserRow {
  id: string;
  username: string;
  email: string;
  role: string;
  full_name: string | null;
  rating: number;
  university_id?: string | null;
  created_at: string;
  updated_at: string;
}

export type AdminRoleParam = "STUDENT" | "TEACHER" | "ADMIN";

export class AdminApiError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
    this.name = "AdminApiError";
  }
}

async function authHeaders(): Promise<HeadersInit> {
  const token = getToken();
  if (!token) {
    throw new AdminApiError(401, "Not authenticated");
  }
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

export async function adminListUsers(params: {
  skip?: number;
  limit?: number;
  role?: string;
}): Promise<AdminUserRow[]> {
  const search = new URLSearchParams();
  search.set("skip", String(params.skip ?? 0));
  search.set("limit", String(params.limit ?? 100));
  if (params.role) {
    search.set("role", params.role);
  }
  const res = await fetch(`${API_URL}/admin?${search.toString()}`, {
    headers: await authHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err?.detail;
    const msg =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg?: string }) => d?.msg).filter(Boolean).join(", ")
          : `Request failed (${res.status})`;
    throw new AdminApiError(res.status, msg || "Failed to load users");
  }
  return res.json();
}

export async function adminChangeUserRole(
  userId: string,
  newRole: AdminRoleParam
): Promise<AdminUserRow> {
  const search = new URLSearchParams({ new_role: newRole });
  const res = await fetch(`${API_URL}/admin/${userId}/role?${search.toString()}`, {
    method: "PUT",
    headers: await authHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err?.detail;
    const msg =
      typeof detail === "string"
        ? detail
        : `Request failed (${res.status})`;
    throw new AdminApiError(res.status, msg || "Failed to update role");
  }
  return res.json();
}
