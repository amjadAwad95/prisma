import { cn } from "@/lib/utils";

export function LoadingSkeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-2xl bg-muted", className)} />;
}

export function CardSkeleton() {
  return (
    <div className="rounded-3xl border border-border bg-card p-6">
      <LoadingSkeleton className="mb-4 h-5 w-1/3" />
      <LoadingSkeleton className="mb-2 h-4 w-2/3" />
      <LoadingSkeleton className="h-32 w-full" />
    </div>
  );
}
