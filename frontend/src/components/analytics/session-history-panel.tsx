"use client";

import { Clock3 } from "lucide-react";
import { useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/services/api";
import { useAnalyticsStore } from "@/store/session-store";
import type { DatasetSession, MethodType, UploadResponseDTO } from "@/types/api";
import { formatBytes } from "@/lib/utils";

export function SessionHistoryPanel() {
  const history = useAnalyticsStore((state) => state.history);
  const activeUploadId = useAnalyticsStore((state) => state.dataset?.uploadId);
  const setHistory = useAnalyticsStore((state) => state.setHistory);
  const setActiveSession = useAnalyticsStore((state) => state.setActiveSession);
  const setAllowedMethods = useAnalyticsStore((state) => state.setAllowedMethods);

  useEffect(() => {
    let isActive = true;
    api.listMetadata()
      .then((uploads) => {
        if (!isActive) return;
        const currentHistory = useAnalyticsStore.getState().history;
        if (!uploads.length) return;
        setHistory(mergeHistory(currentHistory, uploads));
      })
      .catch(() => undefined);
    return () => {
      isActive = false;
    };
  }, [setHistory]);

  const handleSelect = async (session: DatasetSession) => {
    setActiveSession(session.uploadId);
    if (session.methodTypes?.length) {
      setAllowedMethods(session.methodTypes);
      return;
    }
    const allowed = await api.getAllowedMethods(session.uploadId).catch(() => null);
    if (allowed?.method_type?.length) {
      setAllowedMethods(allowed.method_type as MethodType[]);
    }
  };

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
            <button
              key={item.uploadId}
              type="button"
              onClick={() => handleSelect(item)}
              className={`w-full rounded-2xl border border-border bg-background/60 p-3 text-left transition hover:border-primary/40 ${item.uploadId === activeUploadId ? "border-primary/60 bg-primary/10" : ""}`}
            >
              <p className="truncate text-sm font-medium">{item.filename}</p>
              <p className="mt-1 text-xs text-muted-foreground">{formatBytes(item.bytes)} · {new Date(item.uploadedAt).toLocaleString()}</p>
            </button>
          ))
        )}
      </CardContent>
    </Card>
  );
}

function normalizeMethods(input?: string[] | null): MethodType[] {
  const allowed: MethodType[] = ["clustering", "association_rule", "time_series"];
  return (input ?? []).filter((item): item is MethodType => allowed.includes(item as MethodType));
}

function mergeHistory(existing: DatasetSession[], uploads: UploadResponseDTO[]): DatasetSession[] {
  const mergedMap = new Map(existing.map((item) => [item.uploadId, item]));
  uploads.forEach((upload) => {
    const saved = mergedMap.get(upload.upload_id);
    const fallbackMethods = normalizeMethods(upload.method_types);
    const methodTypes = saved?.methodTypes?.length
      ? saved.methodTypes
      : fallbackMethods.length
        ? fallbackMethods
        : ["clustering", "association_rule", "time_series"];
    mergedMap.set(upload.upload_id, {
      uploadId: upload.upload_id,
      filename: upload.filename,
      bytes: upload.bytes,
      contentType: upload.content_type,
      uploadedAt: saved?.uploadedAt ?? new Date().toISOString(),
      methodTypes,
      metadata: saved?.metadata ?? { path: upload.path }
    } satisfies DatasetSession);
  });

  return Array.from(mergedMap.values())
    .sort((a, b) => new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime())
    .slice(0, 12);
}
