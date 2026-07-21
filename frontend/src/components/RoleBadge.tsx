import type { Role } from "../types";

export default function RoleBadge({ role }: { role: Role }) {
  return <span className={`role-badge ${role}`}>{role}</span>;
}
