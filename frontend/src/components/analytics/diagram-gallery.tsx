"use client";

import { Download, Maximize2 } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import type { DiagramsResponseDTO } from "@/types/api";
import { imageToDataUri } from "@/utils/diagrams";
import { EmptyState } from "@/components/feedback/empty-state";

export function DiagramGallery({ diagrams }: { diagrams?: DiagramsResponseDTO | null }) {
  const [selected, setSelected] = useState(0);

  if (!diagrams?.images?.length) {
    return <EmptyState title="No diagrams yet" description="Run an algorithm to fetch generated diagrams from the API." />;
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {diagrams.images.map((image, index) => {
          const src = imageToDataUri(image);
          return (
            <div key={`${image.filename}-${index}`} className="group overflow-hidden rounded-3xl border border-border bg-card shadow-sm">
              <div className="relative aspect-video bg-muted">
                <img src={src} alt={image.filename} loading="lazy" className="h-full w-full object-contain p-3" />
                <div className="absolute inset-x-3 bottom-3 flex translate-y-2 items-center justify-between gap-2 opacity-0 transition group-hover:translate-y-0 group-hover:opacity-100">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button size="sm" variant="secondary" onClick={() => setSelected(index)}>
                        <Maximize2 className="h-4 w-4" /> Preview
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="p-4">
                      <img src={imageToDataUri(diagrams.images[selected])} alt={diagrams.images[selected].filename} className="max-h-[78vh] w-full rounded-2xl object-contain" />
                    </DialogContent>
                  </Dialog>
                  <Button asChild size="sm" variant="outline">
                    <a href={src} download={image.filename}>
                      <Download className="h-4 w-4" /> Download
                    </a>
                  </Button>
                </div>
              </div>
              <div className="px-4 py-3 text-sm font-medium">{image.filename}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
