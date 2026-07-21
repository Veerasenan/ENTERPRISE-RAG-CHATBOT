import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import type { Role } from "../types";

interface Props {
  children: React.ReactNode;
  requiredRoles?: Role[];
}

/**
 * Gates a page by login state, and optionally by role.
 * This is a UX convenience only — the backend independently re-checks
 * every request's role via require_roles(), so this can never be the only guard.
 */
export default function ProtectedRoute({ children, requiredRoles }: Props) {
  const { user, loading } = useAuth();

  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (requiredRoles && !requiredRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}
