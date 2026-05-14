"use client";

import { Clock3 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAnalyticsStore } from "@/store/session-store";
import { formatBytes } from "@/lib/utils";

export function SessionHistoryPanel() {
  const history = useAnalyticsStore((state) => state.history);

  return (
    <Card className="bg-card/75 backdrop-blur-xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base"><Clock3 className="h-4 w-4" /> Session history</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {history.length === 0 ? (
          <p className="text-sm text-muted-foreground">No uploads in this browser session yet.</p>
        ) : (
          history.map((item) => (
            <div key={item.uploadId} className="rounded-2xl border border-border bg-background/60 p-3">
              <p className="truncate text-sm font-medium">{item.filename}</p>
              <p className="mt-1 text-xs text-muted-foreground">{formatBytes(item.bytes)} · {new Date(item.uploadedAt).toLocaleString()}</p>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
