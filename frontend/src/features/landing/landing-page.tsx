"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, BarChart3, Boxes, CheckCircle2, DatabaseZap, FileText, LineChart, Network, ShieldCheck, Sparkles, UploadCloud, Wand2 } from "lucide-react";
import { Navbar } from "@/components/layout/navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AnimatedChartCard } from "@/components/analytics/animated-chart-card";
import { trendData } from "@/utils/demo-data";

const features = [
  { icon: UploadCloud, title: "Dataset ingestion", text: "Drag-and-drop CSV, XLSX, or JSON files with progress, validation, and metadata capture." },
  { icon: Wand2, title: "Smart eligibility", text: "The preprocessing endpoint dynamically enables compatible algorithms after upload." },
  { icon: BarChart3, title: "Visual mining", text: "Polished charts, metrics, diagram galleries, and explainable analysis outputs." },
  { icon: FileText, title: "AI reports", text: "Aggregate session results into markdown reports with print and export workflows." }
];

const algorithms = [
  { icon: Boxes, name: "Clustering", text: "KMeans, DBSCAN, hierarchical, and best algorithm comparison." },
  { icon: Network, name: "Association Rules", text: "Frequent itemsets, lift, confidence, and rule tables." },
  { icon: LineChart, name: "Time Series", text: "Linear regression or ARIMA forecasting with historical plots." }
];

export function LandingPage() {
  return (
    <div className="min-h-screen overflow-hidden bg-radial-premium">
      <Navbar />
      <main>
        <section className="relative">
          <div className="absolute inset-0 bg-grid-pattern bg-[size:42px_42px] opacity-40" />
          <div className="container relative grid min-h-[calc(100vh-4rem)] items-center gap-12 py-20 lg:grid-cols-[1fr_0.9fr]">
            <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
              <Badge variant="outline" className="mb-6 gap-2 bg-background/70 px-4 py-2">
                <Sparkles className="h-3.5 w-3.5 text-primary" /> Smart Analytics Data Mining Platform
              </Badge>
              <h1 className="max-w-4xl text-5xl font-semibold tracking-tight md:text-7xl">
                Turn raw datasets into <span className="gradient-text">mining-ready intelligence</span>.
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
                Upload data, detect compatible algorithms, run mining workflows, visualize diagrams, and generate polished analytics reports from one premium workspace.
              </p>
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Button asChild size="lg" variant="gradient">
                  <Link href="/dashboard">Upload dataset <ArrowRight className="h-4 w-4" /></Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link href="/documentation">View API workflow</Link>
                </Button>
              </div>
              <div className="mt-8 grid max-w-xl gap-3 sm:grid-cols-3">
                {["Session persistence", "Base64 diagrams", "Markdown reports"].map((item) => (
                  <div key={item} className="flex items-center gap-2 text-sm text-muted-foreground">
                    <CheckCircle2 className="h-4 w-4 text-emerald-500" /> {item}
                  </div>
                ))}
              </div>
            </motion.div>
            <motion.div initial={{ opacity: 0, scale: 0.96, y: 24 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ delay: 0.15, duration: 0.7 }} className="relative">
              <div className="absolute -inset-8 -z-10 rounded-full bg-primary/20 blur-3xl" />
              <div className="glass rounded-[2rem] p-4">
                <div className="rounded-[1.5rem] border border-border bg-background/90 p-5 shadow-soft">
                  <div className="mb-5 flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Live workspace</p>
                      <h3 className="text-xl font-semibold">Mining command center</h3>
                    </div>
                    <Badge variant="success">API connected</Badge>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-3">
                    {[
                      ["Datasets", "24"],
                      ["Avg quality", "96%"],
                      ["Reports", "18"]
                    ].map(([label, value]) => (
                      <div key={label} className="rounded-2xl border border-border bg-card p-4">
                        <p className="text-xs text-muted-foreground">{label}</p>
                        <p className="mt-1 text-2xl font-semibold">{value}</p>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4">
                    <AnimatedChartCard title="Algorithm activity" description="Realistic preview of session mining activity." data={trendData} dataKey="clustering" secondaryKey="association" />
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        <section className="container py-24" id="features">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="secondary">Product-grade UX</Badge>
            <h2 className="mt-4 text-4xl font-semibold tracking-tight">Everything needed for end-to-end analysis</h2>
            <p className="mt-4 text-muted-foreground">Built as a component-driven SaaS application with accessibility, responsive design, loading states, empty states, and API retries.</p>
          </div>
          <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div key={feature.title} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: index * 0.08 }}>
                  <Card className="h-full bg-card/70 backdrop-blur-xl">
                    <CardContent className="p-6">
                      <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                        <Icon className="h-5 w-5" />
                      </div>
                      <h3 className="font-semibold">{feature.title}</h3>
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">{feature.text}</p>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </section>

        <section className="container py-20" id="algorithms">
          <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr]">
            <div>
              <Badge variant="outline">Supported algorithms</Badge>
              <h2 className="mt-4 text-4xl font-semibold tracking-tight">Run the right mining method for each dataset.</h2>
              <p className="mt-4 text-muted-foreground">Eligibility is driven by the preprocessing API so unsupported workflows are visible but disabled with clear explanations.</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {algorithms.map((algorithm) => {
                const Icon = algorithm.icon;
                return (
                  <Card key={algorithm.name} className="bg-card/75 backdrop-blur-xl">
                    <CardContent className="p-5">
                      <Icon className="mb-4 h-6 w-6 text-primary" />
                      <h3 className="font-semibold">{algorithm.name}</h3>
                      <p className="mt-2 text-sm leading-6 text-muted-foreground">{algorithm.text}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </section>

        <section className="container py-24">
          <div className="grid gap-5 md:grid-cols-3">
            {[
              ["01", "Upload", "Drop a dataset and capture upload ID, metadata, and method compatibility."],
              ["02", "Analyze", "Run clustering, association, or forecasting with typed API mutations."],
              ["03", "Report", "Collect session outputs into a markdown report with print/export options."]
            ].map(([step, title, text]) => (
              <Card key={step} className="bg-card/75 backdrop-blur-xl">
                <CardContent className="p-6">
                  <div className="text-sm font-semibold text-primary">{step}</div>
                  <h3 className="mt-4 text-xl font-semibold">{title}</h3>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{text}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        <section className="container pb-24">
          <div className="rounded-[2rem] border border-border bg-gradient-to-br from-primary/15 via-sky-500/10 to-fuchsia-500/10 p-8 text-center shadow-soft md:p-14">
            <ShieldCheck className="mx-auto mb-4 h-9 w-9 text-primary" />
            <h2 className="text-4xl font-semibold tracking-tight">Ready to mine smarter?</h2>
            <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">Launch the dashboard, upload a dataset, and let the platform route you to the best compatible analytics workflows.</p>
            <Button asChild size="lg" variant="gradient" className="mt-8">
              <Link href="/dashboard">Open dashboard <ArrowRight className="h-4 w-4" /></Link>
            </Button>
          </div>
        </section>
      </main>
      <footer className="border-t border-border py-8">
        <div className="container flex flex-col justify-between gap-4 text-sm text-muted-foreground md:flex-row">
          <p>© 2026 SmartAnalytics. Premium data mining UI.</p>
          <div className="flex gap-4">
            <Link href="/documentation">Documentation</Link>
            <a href="https://github.com" target="_blank" rel="noreferrer">GitHub</a>
            <a href="mailto:hello@example.com">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
