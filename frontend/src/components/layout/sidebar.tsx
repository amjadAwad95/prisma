"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Bot, Boxes, FileText, Home, LineChart, Network, UploadCloud } from "lucide-react";
import { cn } from "@/lib/utils";

const items = [
  { href: "/dashboard", label: "Workspace", icon: Home },
  { href: "/algorithms/clustering", label: "Clustering", icon: Boxes },
  { href: "/algorithms/association", label: "Association", icon: Network },
  { href: "/algorithms/time-series", label: "Time Series", icon: LineChart },
  { href: "/reports", label: "Reports", icon: FileText }
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden min-h-[calc(100vh-4rem)] w-72 shrink-0 border-r border-border/70 bg-background/65 p-4 backdrop-blur-xl lg:block">
      <div className="mb-5 rounded-3xl border border-border bg-card p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-primary/10 p-3 text-primary">
            <BarChart3 className="h-5 w-5" />
          </div>
          <div>
            <p className="font-semibold">Analysis Studio</p>
            <p className="text-xs text-muted-foreground">Session-based workspace</p>
          </div>
        </div>
      </div>
      <div className="space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-muted-foreground transition hover:bg-muted hover:text-foreground",
                active && "bg-primary text-primary-foreground shadow-lg shadow-primary/20 hover:bg-primary hover:text-primary-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </div>
      <div className="mt-6 rounded-3xl border border-border bg-radial-premium p-4">
        <Bot className="mb-3 h-5 w-5 text-primary" />
        <p className="text-sm font-semibold">Smart method routing</p>
        <p className="mt-1 text-xs leading-5 text-muted-foreground">Upload a file and the API will enable only compatible algorithms.</p>
        <Link href="/dashboard" className="mt-4 flex items-center gap-2 text-xs font-semibold text-primary">
          <UploadCloud className="h-3.5 w-3.5" /> Start upload
        </Link>
      </div>
    </aside>
  );
}
