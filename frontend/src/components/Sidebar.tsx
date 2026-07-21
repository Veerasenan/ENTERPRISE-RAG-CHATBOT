import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import RoleBadge from "./RoleBadge";
import { PRODUCT_NAME, PRODUCT_INITIALS, PRODUCT_TAGLINE } from "../config/product";

export default function Sidebar() {
  const { user, logout } = useAuth();
  if (!user) return null;

  const initials = user.fullName
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">{PRODUCT_INITIALS}</div>
        <div>
          <div className="brand-name">{PRODUCT_NAME}</div>
          <div className="brand-sub">{PRODUCT_TAGLINE}</div>
        </div>
      </div>

      <nav className="nav-section">
        <NavLink to="/" end className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
          💬 Chat
        </NavLink>
        {user.role === "HR" && (
          <NavLink to="/admin" className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
            📁 Manage documents
          </NavLink>
        )}
      </nav>

      <div className="sidebar-footer">
        <div className="user-card">
          <div className="user-avatar">{initials}</div>
          <div className="user-meta">
            <div className="user-name">{user.fullName}</div>
            <div className="user-email">{user.email}</div>
          </div>
        </div>
        <div style={{ padding: "8px 8px 0" }}>
          <RoleBadge role={user.role} />
        </div>
        <button className="logout-btn" onClick={logout}>
          Log out
        </button>
      </div>
    </aside>
  );
}
