export interface MetricResult {
    status: string;
    data: {
      resultType: string;
      result: Array<{
        metric: Record<string, string>;
        values?: [number, string][];
        value?: [number, string];
      }>;
    };
  }