import { AppShell } from "@/components/layout/app-shell";
import { ClusteringClient } from "@/features/algorithms/clustering-client";

export default function ClusteringPage() {
  return (
    <AppShell>
      <ClusteringClient />
    </AppShell>
  );
}
