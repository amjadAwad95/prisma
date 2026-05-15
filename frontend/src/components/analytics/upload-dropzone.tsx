"use client";

import { useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { FileSpreadsheet, UploadCloud } from "lucide-react";
import { useCallback, useRef, useState } from "react";
import { toast } from "sonner";
import { Progress } from "@/components/ui/progress";
import { api } from "@/services/api";
import { useAnalyticsStore } from "@/store/session-store";
import type { MethodType } from "@/types/api";
import { formatBytes } from "@/lib/utils";

const acceptedExtensions = [".csv", ".xlsx", ".json"];

function normalizeMethods(input?: string[] | null): MethodType[] {
  const allowed: MethodType[] = ["clustering", "association_rule", "time_series"];
  return (input ?? []).filter((item): item is MethodType => allowed.includes(item as MethodType));
}

export function UploadDropzone() {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [progress, setProgress] = useState(0);
  const { setDataset, setAllowedMethods } = useAnalyticsStore();

  const mutation = useMutation({
    mutationFn: async (file: File) => {
      setProgress(0);
      const upload = await api.uploadFile(file, setProgress);
      const methods = await api.getAllowedMethods(upload.upload_id).catch(() => ({ method_type: normalizeMethods(upload.method_types) }));
      return { upload, methodTypes: methods.method_type };
    },
    onSuccess: ({ upload, methodTypes }) => {
      setDataset({
        uploadId: upload.upload_id,
        filename: upload.filename,
        bytes: upload.bytes,
        contentType: upload.content_type,
        uploadedAt: new Date().toISOString(),
        methodTypes: methodTypes.length ? methodTypes : normalizeMethods(upload.method_types),
        metadata: upload.metadata ?? { path: upload.path }
      });
      setAllowedMethods(methodTypes);
      toast.success("Dataset uploaded and profiled", { description: "Compatible algorithms are now enabled." });
    },
    onError: (error) => {
      toast.error("Upload failed", { description: error instanceof Error ? error.message : "Please try again." });
    }
  });

  const handleFile = useCallback((file?: File) => {
    if (!file) return;
    const extension = `.${file.name.split(".").pop()?.toLowerCase() ?? ""}`;
    if (!acceptedExtensions.includes(extension)) {
      toast.error("Unsupported file type", { description: "Upload CSV, XLSX, or JSON files only." });
      return;
    }
    mutation.mutate(file);
  }, [mutation]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      onDragEnter={(event) => {
        event.preventDefault();
        setDragActive(true);
      }}
      onDragOver={(event) => event.preventDefault()}
      onDragLeave={() => setDragActive(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragActive(false);
        handleFile(event.dataTransfer.files[0]);
      }}
      className={`relative overflow-hidden rounded-3xl border border-dashed p-8 transition ${dragActive ? "border-primary bg-primary/10" : "border-border bg-card/70"}`}
    >
      <div className="absolute inset-0 bg-grid-pattern bg-[size:28px_28px] opacity-40" />
      <div className="relative flex flex-col items-center text-center">
        <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-3xl bg-gradient-to-br from-indigo-500 via-sky-500 to-fuchsia-500 text-white shadow-glow">
          <UploadCloud className="h-7 w-7" />
        </div>
        <h2 className="text-2xl font-semibold">Upload a dataset</h2>
        <p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">Drop a CSV, XLSX, or JSON file. The platform will profile metadata, call preprocessing eligibility, and unlock compatible mining workflows.</p>
        <button
          type="button"
          className="mt-6 rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/20 transition hover:-translate-y-0.5"
          onClick={() => inputRef.current?.click()}
        >
          Choose file
        </button>
        <input ref={inputRef} type="file" className="sr-only" accept=".csv,.xlsx,.json" onChange={(event) => handleFile(event.target.files?.[0])} />
        {mutation.isPending ? (
          <div className="mt-6 w-full max-w-md">
            <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
              <span>Uploading and analyzing</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} />
          </div>
        ) : null}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3 text-xs text-muted-foreground">
          {acceptedExtensions.map((extension) => (
            <span key={extension} className="inline-flex items-center gap-1 rounded-full border border-border bg-background/70 px-3 py-1">
              <FileSpreadsheet className="h-3.5 w-3.5" /> {extension.toUpperCase()} up to {formatBytes(50 * 1024 * 1024)}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
