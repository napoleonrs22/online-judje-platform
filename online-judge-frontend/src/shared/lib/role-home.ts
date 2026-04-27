export type AppRole = "student" | "teacher" | "admin";

export function normalizeRole(role: string): AppRole {
  const r = role.toLowerCase();
  if (r === "teacher") return "teacher";
  if (r === "admin") return "admin";
  return "student";
}

/** After login — overview / “my space” */
export function getPostLoginPath(role: string): string {
  switch (normalizeRole(role)) {
    case "admin":
      return "/dashboard/admin";
    case "teacher":
      return "/dashboard/teacher";
    default:
      return "/dashboard";
  }
}

/** “Start coding” entry — students go to challenges */
export function getStartCodingPath(role: string): string {
  switch (normalizeRole(role)) {
    case "admin":
      return "/dashboard/admin";
    case "teacher":
      return "/dashboard/teacher";
    default:
      return "/dashboard/challenges";
  }
}

export function canSeeTeacherNav(role: string): boolean {
  const n = normalizeRole(role);
  return n === "teacher" || n === "admin";
}

export function canSeeAdminNav(role: string): boolean {
  return normalizeRole(role) === "admin";
}
