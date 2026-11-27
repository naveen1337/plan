import { MetricCard } from "../../components/metric-cards/react/metric-card";
import type { HomeMetric } from "./home_ctrl";

export interface HomeUiProps {
  metrics: HomeMetric[];
}

export function HomeUi({ metrics }: HomeUiProps) {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-light">Project info</h1>
        <p className="mt-1 text-sm text-muted">
          Track task progress across planning, execution, and review.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {metrics.map((metric) => (
          <MetricCard
            key={metric.id}
            title={metric.title}
            value={metric.value}
            caption={metric.caption}
            accent={metric.accent}
            theme="dark"
          />
        ))}
      </div>
    </div>
  );
}
