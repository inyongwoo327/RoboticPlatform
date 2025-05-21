// src/stores/logStore.ts
import { defineStore } from 'pinia';
import axios from 'axios';

interface Log {
  timestamp: string;
  level: string;
  message: string;
  kubernetes?: {
    pod_name: string;
    container_name: string;
  };
  index?: number;
}

interface LogFilter {
  level: string;
  timestamp: string;
}

export const useLogStore = defineStore('log', {
  state: () => ({
    logs: [] as Log[],
    filteredLogs: [] as Log[],
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
            kubernetes: log.kubernetes,
            index
          }));
          
          // Apply filters to the fetched logs
          this.applyFilters();
        }
      } catch (error: any) {
        this.error = error.message || 'Failed to fetch logs';
        console.error(this.error);
        
        // fallback
        this.filteredLogs = this.logs;
      } finally {
        this.loading = false;
      }
    },
    
    updateLogFilter(filter: { level: string, timestamp: string }) {
      this.filter = { ...this.filter, ...filter };
      
      // Apply filters to already fetched logs
      this.applyFilters();
      
      // Only fetch from backend if needed (optional)
      // if (filter.level || filter.timestamp) {
      //   this.fetchLogs();
      // }
    },
    
    applyFilters() {
      console.log('Applying filters:', this.filter);
      console.log('Sample log timestamp:', this.logs.length > 0 ? this.logs[0].timestamp : 'No logs');
      
      this.filteredLogs = this.logs.filter(log => {
        // Level filter - case insensitive partial match
        const levelMatch = !this.filter.level || 
                          log.level.toLowerCase().includes(this.filter.level.toLowerCase());
        
        // Timestamp filter
        let timestampMatch = true;
        if (this.filter.timestamp && this.filter.timestamp.trim() !== '') {
          const filterText = this.filter.timestamp.trim();
          
          timestampMatch = (
            log.timestamp.includes(filterText) ||                // Direct match
            log.timestamp.split('T')[0].includes(filterText) ||  // Date part only
            log.timestamp.split('T')[1].includes(filterText)     // Time part only
          );
        }
        
        return levelMatch && timestampMatch;
      });
      
      console.log('Filtered logs count:', this.filteredLogs.length);
    }
  },
  
  getters: {
    getFilteredLogs(): Log[] {
      return this.filteredLogs;
    }
  }
});