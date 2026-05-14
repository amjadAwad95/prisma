"use client";

import Link from "next/link";
import type { MethodType } from "@/types/api";
import { EmptyState } from "@/components/feedback/empty-state";
import { Button } from "@/components/ui/button";
import { useAnalyticsStore } from "@/store/session-store";

export function AlgorithmGuard({ method, children }: { method: MethodType; children: React.ReactNode }) {
  const dataset = useAnalyticsStore((state) => state.dataset);
  if (!dataset) {
    return <EmptyState title="Upload a dataset first" description="Algorithm workflows require an active upload ID from the dashboard." actionLabel="Go to dashboard" onAction={() => window.location.assign("/dashboard")} />;
  }

  if (!dataset.methodTypes.includes(method)) {
    return (
      <div className="space-y-4">
        <EmptyState title="Algorithm not compatible" description="The preprocessing endpoint did not enable this workflow for the active dataset. Try uploading a different dataset or run another supported workflow." />
        <Button asChild variant="outline"><Link href="/dashboard">Review compatible algorithms</Link></Button>
      </div>
    );
  }

  return <>{children}</>;
}
