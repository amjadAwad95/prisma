"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";
import { ArrowRight, Lock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

export function AlgorithmCard({
  title,
  description,
  href,
  icon: Icon,
  enabled,
  reason,
  badge
}: {
  title: string;
  description: string;
  href: string;
  icon: LucideIcon;
  enabled: boolean;
  reason?: string;
  badge?: string;
}) {
  const content = (
    <motion.div whileHover={enabled ? { y: -6, scale: 1.01 } : {}} transition={{ type: "spring", stiffness: 260, damping: 18 }}>
      <Card className={cn("relative h-full overflow-hidden bg-card/75 backdrop-blur-xl transition", !enabled && "opacity-55 grayscale")}> 
        <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-indigo-500 via-sky-500 to-fuchsia-500" />
        <CardContent className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div className="rounded-2xl bg-primary/10 p-3 text-primary">
              <Icon className="h-6 w-6" />
            </div>
            <Badge variant={enabled ? "success" : "warning"}>{enabled ? badge ?? "Enabled" : "Disabled"}</Badge>
          </div>
          <h3 className="mt-5 text-xl font-semibold">{title}</h3>
          <p className="mt-2 min-h-12 text-sm leading-6 text-muted-foreground">{description}</p>
          <Button disabled={!enabled} className="mt-6 w-full" variant={enabled ? "gradient" : "outline"} asChild={enabled}>
            {enabled ? (
              <Link href={href}>Open workflow <ArrowRight className="h-4 w-4" /></Link>
            ) : (
              <span><Lock className="h-4 w-4" /> Waiting for compatible dataset</span>
            )}
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );

  if (enabled) return content;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>{content}</TooltipTrigger>
        <TooltipContent>{reason ?? "Upload a compatible dataset to enable this algorithm."}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
