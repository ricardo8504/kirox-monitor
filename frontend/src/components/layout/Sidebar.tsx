import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Server,
  Bell,
  Settings,
  Activity,
} from "lucide-react";
import { useAuthStore } from "@/stores/authStore";

const NAV_ITEMS = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/servers", icon: Server, label: "Servers" },
  { to: "/alerts", icon: Bell, label: "Alerts" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export function Sidebar() {
  const user = useAuthStore((s) => s.user);

  return (
    <aside className="flex flex-col w-56 min-h-screen bg-gray-900 border-r border-gray-800">
      <div className="flex items-center gap-2 px-4 py-5 border-b border-gray-800">
        <Activity className="w-6 h-6 text-brand-500" />
        <span className="font-bold text-white text-sm tracking-wide">
          Odoo Monitor
        </span>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-brand-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              }`
            }
          >
            <Icon className="w-4 h-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      {user && (
        <div className="px-4 py-3 border-t border-gray-800">
          <p className="text-xs text-gray-400 truncate">{user.email}</p>
          <p className="text-xs text-gray-600 capitalize">{user.role}</p>
        </div>
      )}
    </aside>
  );
}
