"use client";

import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { ArrowUpRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function MetricCard({ title, value, delta, icon: Icon, className, onClick }: { title: string; value: string | number; delta?: string; icon: LucideIcon; className?: string; onClick?: () => void }) {
  return (
    <motion.div whileHover={{ y: -4 }} transition={{ type: "spring", stiffness: 260, damping: 20 }}>
      <Card className={cn("overflow-hidden bg-card/75 backdrop-blur-xl", className)} onClick={onClick}>
        <CardContent className="p-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-muted-foreground">{title}</p>
              <p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p>
            </div>
            <div className="rounded-2xl bg-primary/10 p-3 text-primary">
              <Icon className="h-5 w-5" />
            </div>
          </div>
          {delta ? (
            <div className="mt-4 inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-600 dark:text-emerald-300">
              <ArrowUpRight className="h-3.5 w-3.5" /> {delta}
            </div>
          ) : null}
        </CardContent>
      </Card>
    </motion.div>
  );
}
