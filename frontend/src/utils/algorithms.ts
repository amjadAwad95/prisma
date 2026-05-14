import { Boxes, Layers3, LineChart, Network } from "lucide-react";
import type { MethodType } from "@/types/api";

export const algorithmCatalog = [
  {
    method: "clustering" as MethodType,
    title: "Clustering",
    href: "/algorithms/clustering",
    icon: Boxes,
    badge: "KMeans · DBSCAN",
    description: "Segment observations into coherent groups and compare the best clustering strategy."
  },
  {
    method: "association_rule" as MethodType,
    title: "Association Rules",
    href: "/algorithms/association",
    icon: Network,
    badge: "Apriori rules",
    description: "Discover frequent itemsets, confidence, lift, and explainable co-occurrence rules."
  },
  {
    method: "pca" as MethodType,
    title: "Principal Component Analysis",
    href: "/algorithms/pca",
    icon: Layers3,
    badge: "Variance mapping",
    description: "Reduce dimensionality while preserving variance and inspecting component quality."
  },
  {
    method: "time_series" as MethodType,
    title: "Time Series Forecasting",
    href: "/algorithms/time-series",
    icon: LineChart,
    badge: "ARIMA · Linear",
    description: "Forecast trends from temporal data with historical and predicted value plots."
  }
];

export function methodLabel(method: MethodType) {
  switch (method) {
    case "association_rule":
      return "Association Rule Mining";
    case "time_series":
      return "Time Series";
    default:
      return method.charAt(0).toUpperCase() + method.slice(1);
  }
}
