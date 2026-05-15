import { Boxes, LineChart, Network } from "lucide-react";
import type { MethodType } from "@/types/api";

export const algorithmCatalog = [
  {
    method: "clustering" as MethodType,
    title: "Clustering",
    href: "/algorithms/clustering",
    icon: Boxes,
    badge: "Best clustering",
    description: "Run all clustering methods automatically and return the best grouping."
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
