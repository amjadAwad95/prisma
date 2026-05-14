import { AppShell } from "@/components/layout/app-shell";
import { PCAClient } from "@/features/algorithms/pca-client";

export default function PCAPage() {
  return (
    <AppShell>
      <PCAClient />
    </AppShell>
  );
}
