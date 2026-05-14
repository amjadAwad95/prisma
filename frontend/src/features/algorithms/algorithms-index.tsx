"use client";

import { AlgorithmCard } from "@/components/analytics/algorithm-card";
import { Badge } from "@/components/ui/badge";
import { useAnalyticsStore } from "@/store/session-store";
import { algorithmCatalog } from "@/utils/algorithms";

export function AlgorithmsIndex() {
  const dataset = useAnalyticsStore((state) => state.dataset);
  const allowed = dataset?.methodTypes ?? [];

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <div>
        <Badge variant="outline">Algorithm Studio</Badge>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight">Choose a mining workflow</h1>
        <p className="mt-2 max-w-2xl text-muted-foreground">Cards are dynamically enabled after upload based on the `/preprocessing/type/{'{upload_id}'}` response.</p>
      </div>
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {algorithmCatalog.map((algorithm) => (
          <AlgorithmCard
            key={algorithm.method}
            {...algorithm}
            enabled={allowed.includes(algorithm.method)}
            reason={dataset ? "This algorithm is not compatible with the active dataset." : "Upload a dataset in the dashboard first."}
          />
        ))}
      </div>
    </div>
  );
}
