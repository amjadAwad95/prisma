"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/algorithms", label: "Algorithms" },
  { href: "/reports", label: "Reports" },
  { href: "/documentation", label: "Documentation" }
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-40 border-b border-border/60 bg-background/75 backdrop-blur-2xl">
      <div className="container flex h-16 items-center justify-between gap-4">
        <Link href="/" className="flex items-center gap-3 font-semibold">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 via-sky-500 to-fuchsia-500 text-white shadow-glow">
            <BarChart3 className="h-5 w-5" />
          </span>
          <span className="hidden sm:block">SmartAnalytics</span>
        </Link>
        <div className="hidden items-center gap-1 rounded-full border border-border bg-muted/40 p-1 lg:flex">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "rounded-full px-4 py-2 text-sm text-muted-foreground transition hover:text-foreground",
                pathname === item.href && "bg-background text-foreground shadow-sm"
              )}
            >
              {item.label}
            </Link>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button asChild variant="gradient" className="hidden sm:inline-flex">
            <Link href="/dashboard">
              <UploadCloud className="h-4 w-4" /> Upload Dataset
            </Link>
          </Button>
        </div>
      </div>
    </nav>
  );
}
