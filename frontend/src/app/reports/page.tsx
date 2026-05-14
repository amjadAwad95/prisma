import { AppShell } from "@/components/layout/app-shell";
import { ReportsClient } from "@/features/reports/reports-client";

export default function ReportsPage() {
  return (
    <AppShell>
      <ReportsClient />
    </AppShell>
  );
}
