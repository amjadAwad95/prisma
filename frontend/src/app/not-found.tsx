import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-radial-premium p-6 text-center">
      <div className="max-w-md rounded-3xl border border-border bg-card p-8 shadow-soft">
        <p className="text-sm font-semibold text-primary">404</p>
        <h1 className="mt-2 text-3xl font-semibold">Page not found</h1>
        <p className="mt-3 text-muted-foreground">The analytics route you requested does not exist.</p>
        <Button asChild className="mt-6" variant="gradient"><Link href="/dashboard">Back to dashboard</Link></Button>
      </div>
    </div>
  );
}
