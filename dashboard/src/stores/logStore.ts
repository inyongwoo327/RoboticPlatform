// Create a new file: src/stores/logStore.ts
import { defineStore } from 'pinia';
import axios from 'axios';

interface Log {
  timestamp: string;
  level: string;
  message: string;
  index?: number;
}

interface LogFilter {
  level: string;
  timestamp: string;
}

export const useLogStore = defineStore('log', {
  state: () => ({
    logs: [] as Log[],
    filter: { level: '', timestamp: '' } as LogFilter,
    loading: false,
    error: null as string | null,
  }),
  
  actions: {
    async fetchLogs() {
      this.loading = true;
      this.error = null;
      try {
        const LOG_API_URL = 'http://log-api.local';
        const params = {
          level: this.filter.level || undefined,
          timestamp: this.filter.timestamp || undefined
        };
        
        const response = await axios.get(`${LOG_API_URL}/logs`, { params });
        
        if (response.data && response.data.logs) {
          this.logs = response.data.logs.map((log: any, index: number) => ({
            timestamp: log.timestamp || new Date().toISOString(),
            level: log.level || 'info',
            message: log.message || log.log || JSON.stringify(log),
            index
          }));
        }
      } catch (error: any) {
        this.error = error.message || 'Failed to fetch logs';
        console.error(this.error);
      } finally {
        this.loading = false;
      }
    },
    
    updateLogFilter(filter: { level: string, timestamp: string }) {
      this.filter = { ...this.filter, ...filter };
      this.fetchLogs();
    }
  }
});