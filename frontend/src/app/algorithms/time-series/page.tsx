import { AppShell } from "@/components/layout/app-shell";
import { TimeSeriesClient } from "@/features/algorithms/time-series-client";

export default function TimeSeriesPage() {
  return (
    <AppShell>
      <TimeSeriesClient />
    </AppShell>
  );
}
