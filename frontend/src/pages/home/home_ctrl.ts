import type { MetricCardAccent } from "../../components/metric-cards/react/metric-card";

export interface HomeMetric {
  id: string;
  title: string;
  value: string;
  caption: string;
  accent?: MetricCardAccent;
}

export const HOME_PRODUCT_NAME = "Plan and Execution";

export const HOME_METRICS: HomeMetric[] = [
  {
    id: "tasks",
    title: "Tasks",
    value: "24",
    caption: "Total tasks",
    accent: "primary",
  },
  {
    id: "planned",
    title: "Planned",
    value: "8",
    caption: "Ready to start",
    accent: "secondary",
  },
  {
    id: "in-progress",
    title: "In Progress",
    value: "6",
    caption: "Currently active",
    accent: "warning",
  },
  {
    id: "review",
    title: "Review",
    value: "4",
    caption: "Awaiting review",
    accent: "primary",
  },
  {
    id: "completed",
    title: "Completed",
    value: "6",
    caption: "Finished this cycle",
    accent: "success",
  },
];
