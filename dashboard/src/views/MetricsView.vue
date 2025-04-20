<template>
  <div class="section">
    <h2>Metrics</h2>
    
    <div class="metrics-controls">
      <select v-model="selectedMetric" @change="fetchMetricData">
        <option value="robots_added_total">Robots Added</option>
        <option value="request_duration_seconds_count">Request Count</option>
        <option value="request_duration_seconds_sum">Request Duration</option>
      </select>
      
      <select v-model="timeRange" @change="fetchMetricData">
        <option value="5m">Last 5 minutes</option>
        <option value="15m">Last 15 minutes</option>
        <option value="1h">Last hour</option>
        <option value="3h">Last 3 hours</option>
      </select>
    </div>
    
    <div class="chart-container">
      <div v-if="loading" class="loading">Loading metrics data...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="chartData.length === 0" class="no-data">No metrics data available for the selected period</div>
      <canvas v-else ref="chartRef"></canvas>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted, watch } from 'vue';
import { useRobotStore } from '../stores/robotStore';
import { Chart } from 'chart.js/auto';
import axios from 'axios';

export default defineComponent({
  name: 'MetricsView',
  setup() {
    const store = useRobotStore();
    const chartRef = ref<HTMLCanvasElement | null>(null);
    const chart = ref<any>(null);
    const selectedMetric = ref('robots_added_total');
    const timeRange = ref('15m');
    const chartData = ref<number[]>([]);
    const chartLabels = ref<string[]>([]);
    const loading = ref(false);
    const error = ref('');
    let refreshInterval: number | null = null;

    const PROMETHEUS_URLS = [
      'http://prometheus:9090',
      'http://prometheus.local',
      'http://prometheus.default.svc.cluster.local:9090',
      '/prometheus'
    ];
    
    const urlIndex = ref(0);

    const parseTimeRange = (range: string): number => {
      const value = parseInt(range);
      const unit = range.slice(-1);
      
      switch(unit) {
        case 'm': return value * 60;
        case 'h': return value * 60 * 60;
        case 'd': return value * 24 * 60 * 60;
        default: return value;
      }
    };

    const fetchMetricData = async () => {
      loading.value = true;
      error.value = '';
      try {
        const now = Math.floor(Date.now() / 1000);
        const timeRangeInSeconds = parseTimeRange(timeRange.value);
        const start = now - timeRangeInSeconds;
        const step = Math.max(Math.floor(timeRangeInSeconds / 30), 15);

        console.log(`Fetching metrics from: ${PROMETHEUS_URLS[urlIndex.value]}`);
        
        const response = await axios.get(`${PROMETHEUS_URLS[urlIndex.value]}/api/v1/query_range`, {
          params: {
            query: selectedMetric.value,
            start,
            end: now,
            step
          }
        });
        
        console.log('Prometheus response:', response.data);
        
        if (response.data.status === 'success' && response.data.data?.result?.length > 0) {
          const result = response.data.data.result[0];
          chartData.value = result.values.map((v: [number, string]) => Number(v[1]));
          chartLabels.value = result.values.map((v: [number, string]) => new Date(v[0] * 1000).toLocaleTimeString());
        } else {
          chartData.value = [];
          chartLabels.value = [];
        }
      } catch (err: any) {
        console.error('Error fetching metrics:', err);
        error.value = `Failed to fetch metrics: ${err.message}`;
        
        // Try the next URL if available
        if (urlIndex.value < PROMETHEUS_URLS.length - 1) {
          urlIndex.value++;
          console.log(`Trying next Prometheus URL: ${PROMETHEUS_URLS[urlIndex.value]}`);
          await fetchMetricData();
          return;
        }
        
        // If we've tried all URLs and none worked, create some mock data for the demo
        chartLabels.value = [];
        chartData.value = [];
        const now = new Date();
        for (let i = 0; i < 10; i++) {
          const time = new Date(now.getTime() - (i * 60000));
          chartLabels.value.unshift(time.toLocaleTimeString());
          chartData.value.unshift(Math.floor(Math.random() * 3) + 1); // Random value 1-3
        }
        console.log('Using mock data for demonstration');
      } finally {
        loading.value = false;
        updateChart();
      }
    };

    const createChart = () => {
      if (!chartRef.value) return;
      
      const ctx = chartRef.value.getContext('2d');
      if (!ctx) return;
      
      chart.value = new Chart(ctx, {
        type: 'line',
        data: {
          labels: chartLabels.value,
          datasets: [{
            label: formatMetricName(selectedMetric.value),
            data: chartData.value,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            tension: 0.1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          },
          animation: {
            duration: 500
          }
        }
      });
    };

    const updateChart = () => {
      if (chart.value) {
        chart.value.destroy();
      }
      createChart();
    };

    const formatMetricName = (name: string): string => {
      return name
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
    };

    onMounted(() => {
      fetchMetricData();
      refreshInterval = window.setInterval(() => {
        fetchMetricData();
      }, 30000);
    });

    onUnmounted(() => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
      if (chart.value) {
        chart.value.destroy();
      }
    });

    watch([selectedMetric, timeRange], () => {
      fetchMetricData();
    });

    return {
      store,
      chartRef,
      selectedMetric,
      timeRange,
      chartData,
      chartLabels,
      loading,
      error,
      fetchMetricData
    };
  }
});
</script>

<style scoped>
.section {
  margin-bottom: 40px;
}

h2 {
  margin-top: 0;
  margin-bottom: 20px;
}

.metrics-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

select {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.chart-container {
  height: 400px;
  position: relative;
}

.loading, .error, .no-data {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.error {
  color: #dc3545;
}

.no-data {
  color: #6c757d;
}
</style>