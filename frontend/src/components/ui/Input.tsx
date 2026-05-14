import { type InputHTMLAttributes, forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, id, className = "", ...props }, ref) => (
    <div className="space-y-1">
      {label && (
        <label htmlFor={id} className="block text-xs font-medium text-gray-400">
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={id}
        className={`w-full bg-gray-800 border rounded-md px-3 py-2 text-sm text-white placeholder-gray-500 transition-colors focus:outline-none focus:ring-1 ${
          error
            ? "border-red-500 focus:ring-red-500"
            : "border-gray-700 focus:ring-brand-500"
        } ${className}`}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        {...props}
      />
      {error && (
        <p id={`${id}-error`} role="alert" className="text-xs text-red-400">
          {error}
        </p>
      )}
      {hint && !error && (
        <p id={`${id}-hint`} className="text-xs text-gray-500">
          {hint}
        </p>
      )}
    </div>
  ),
);
Input.displayName = "Input";
