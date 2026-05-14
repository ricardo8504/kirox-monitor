import { Bell, LogOut } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="h-14 flex items-center justify-between px-6 bg-gray-900 border-b border-gray-800 shrink-0">
      <div />
      <div className="flex items-center gap-4">
        <button
          type="button"
          className="p-1.5 rounded-md text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
        </button>
        {user && (
          <span className="text-sm text-gray-300 hidden sm:block">
            {user.username}
          </span>
        )}
        <button
          type="button"
          onClick={() => void logout()}
          className="p-1.5 rounded-md text-gray-400 hover:text-red-400 hover:bg-gray-800 transition-colors"
          aria-label="Logout"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}
