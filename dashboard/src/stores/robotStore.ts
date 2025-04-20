import { defineStore } from 'pinia';
import { Robot, RobotUpdate } from '../models/Robot';
import robotService from '../services/robotService';
import axios from 'axios';

interface MetricPoint {
  time: string;
  value: number;
}

export const useRobotStore = defineStore('robot', {
  state: () => ({
    robots: [] as Robot[],
    metrics: [] as MetricPoint[],
    loading: false,
    error: null as string | null,
  }),
  
  actions: {
    async fetchRobots() {
      this.loading = true;
      this.error = null;
      try {
        const response = await robotService.getAllRobots();
        this.robots = response.data;
      } catch (err: any) {
        this.error = err.message || 'Failed to fetch robots';
        console.error(this.error);
      } finally {
        this.loading = false;
      }
    },
    
    async addRobot(robot: Robot) {
      this.loading = true;
      this.error = null;
      try {
        await robotService.addRobot(robot);
        await this.fetchRobots();
      } catch (err: any) {
        this.error = err.message || 'Failed to add robot';
        console.error(this.error);
        throw err;
      } finally {
        this.loading = false;
      }
    },
    
    async updateRobot(id: string, updates: RobotUpdate) {
      this.loading = true;
      this.error = null;
      try {
        await robotService.updateRobot(id, updates);
        await this.fetchRobots();
      } catch (err: any) {
        this.error = err.message || 'Failed to update robot';
        console.error(this.error);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchMetrics() {
      try {
        const PROMETHEUS_URL = 'http://prometheus.default.svc.cluster.local:9090';
        const now = Math.floor(Date.now() / 1000);
        const timeAgo = now - 3600; // Get data for the last hour
        
        const response = await axios.get(`${PROMETHEUS_URL}/api/v1/query_range`, {
          params: {
            query: 'robots_added_total',
            start: timeAgo,
            end: now,
            step: '60s' // 1-minute intervals
          }
        });
        
        if (response.data.status === 'success' && response.data.data?.result?.length > 0) {
          const result = response.data.data.result[0];
          
          this.metrics = result.values.map((item: [number, string]) => ({
            time: new Date(item[0] * 1000).toLocaleTimeString(),
            value: Number(item[1])
          }));
        }
      } catch (error: any) {
        console.error('Error fetching metrics:', error);
        // Not setting this.error here to avoid affecting the UI for robot operations
      }
    }
  }
});