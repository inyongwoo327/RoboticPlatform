import { defineStore } from 'pinia';
import axios from 'axios';

interface Robot {
  id: string;
  name: string;
  status: string;
}

interface Metric {
  time: string;
  value: number;
}

interface Log {
  timestamp: string;
  level: string;
  message: string;
}

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    robots: [] as Robot[],
    metrics: [] as Metric[],
    logs: [] as Log[],
    logFilter: { level: '', timestamp: '' },
  }),
  actions: {
    async fetchRobots() {
      try {
        const res = await axios.get('http://robot.local/robots');
        this.robots = res.data;
      } catch (error) {
        console.error('Error fetching robots:', error);
      }
    },
    async addRobot(robot: Robot) {
      try {
        await axios.post('http://robot.local/robots', robot);
        await this.fetchRobots();
      } catch (error) {
        console.error('Error adding robot:', error);
      }
    },
    async fetchMetrics() {
      try {
        const res = await axios.get('http://prometheus.local/api/v1/query?query=robots_added_total');
        const data = res.data.data.result.flatMap((r: any) =>
          r.values.map(([time, value]: [number, string]) => ({
            time: new Date(time * 1000).toLocaleTimeString(),
            value: parseFloat(value),
          }))
        );
        this.metrics = data;
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    },
    async fetchLogs() {
      // Placeholder; replace with Elasticsearch API
      this.logs = [
        { timestamp: new Date().toISOString(), level: 'INFO', message: 'Sample log' },
      ];
    },
    updateLogFilter(filter: { level: string; timestamp: string }) {
      this.logFilter = filter;
      this.fetchLogs();
    },
  },
});