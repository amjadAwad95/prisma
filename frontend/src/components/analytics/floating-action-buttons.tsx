"use client";

import Link from "next/link";
import { FileText, UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";

export function FloatingActionButtons() {
  return (
    <div className="no-print fixed bottom-5 right-5 z-30 flex flex-col gap-2">
      <Button asChild variant="gradient" size="icon" aria-label="Upload dataset">
        <Link href="/dashboard"><UploadCloud className="h-5 w-5" /></Link>
      </Button>
      <Button asChild variant="outline" size="icon" aria-label="Generate report">
        <Link href="/reports"><FileText className="h-5 w-5" /></Link>
      </Button>
    </div>
  );
}
