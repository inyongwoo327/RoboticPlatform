export interface Log {
    timestamp?: string;
    log?: string;
    message?: string;
    level?: string;
    kubernetes?: {
      pod_name: string;
      container_name: string;
      labels: Record<string, string>;
    };
    [key: string]: any;
  }
  
  export interface LogSearchResult {
    total: number;
    logs: Log[];
  }