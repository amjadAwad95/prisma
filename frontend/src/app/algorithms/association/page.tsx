import { AppShell } from "@/components/layout/app-shell";
import { AssociationClient } from "@/features/algorithms/association-client";

export default function AssociationPage() {
  return (
    <AppShell>
      <AssociationClient />
    </AppShell>
  );
}
