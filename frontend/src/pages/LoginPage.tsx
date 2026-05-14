import { useState, type FormEvent } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Activity } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export function LoginPage() {
  const { login, isLoggingIn, loginError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname ?? "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await login({ email, password });
      navigate(from, { replace: true });
    } catch {
      // error shown via loginError
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 p-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2 mb-8">
          <Activity className="w-8 h-8 text-brand-500" />
          <span className="text-xl font-bold text-white">Odoo Monitor</span>
        </div>

        <form
          onSubmit={(e) => void handleSubmit(e)}
          className="bg-gray-900 rounded-xl p-6 space-y-4 border border-gray-800"
        >
          <h1 className="text-lg font-semibold text-white text-center">Sign in</h1>

          {loginError && (
            <p className="text-sm text-red-400 text-center">
              Invalid credentials. Please try again.
            </p>
          )}

          <div className="space-y-1">
            <label htmlFor="email" className="block text-xs text-gray-400">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div className="space-y-1">
            <label htmlFor="password" className="block text-xs text-gray-400">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-md px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <button
            type="submit"
            disabled={isLoggingIn}
            className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-60 text-white text-sm font-medium rounded-md py-2 transition-colors"
          >
            {isLoggingIn ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
