interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const SIZE_CLASSES = { sm: "w-4 h-4", md: "w-8 h-8", lg: "w-12 h-12" };

export function Spinner({ size = "md", className = "" }: SpinnerProps) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={`border-2 border-gray-700 border-t-brand-500 rounded-full animate-spin ${SIZE_CLASSES[size]} ${className}`}
    />
  );
}
