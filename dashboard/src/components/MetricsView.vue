<template>
    <div class="section">
      <h2>Metrics</h2>
      <canvas ref="chartCanvas"></canvas>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, onMounted, watch } from 'vue';
  import Chart from 'chart.js/auto';
  import { useDashboardStore } from '../stores/dashboard';
  
  export default defineComponent({
    name: 'MetricsView',
    setup() {
      const store = useDashboardStore();
      const chartCanvas = ref<HTMLCanvasElement | null>(null);
      let chart: Chart | null = null;
  
      const updateChart = () => {
        if (chartCanvas.value && store.metrics.length) {
          if (chart) chart.destroy();
          chart = new Chart(chartCanvas.value, {
            type: 'line',
            data: {
              labels: store.metrics.map(m => m.time),
              datasets: [
                {
                  label: 'Robots Added',
                  data: store.metrics.map(m => m.value),
                  borderColor: '#8884d8',
                  fill: false,
                },
              ],
            },
            options: {
              responsive: true,
              scales: {
                x: { title: { display: true, text: 'Time' } },
                y: { title: { display: true, text: 'Count' } },
              },
            },
          });
        }
      };
  
      onMounted(() => {
        store.fetchMetrics();
        setInterval(store.fetchMetrics, 5000);
        updateChart();
      });
  
      watch(() => store.metrics, updateChart, { deep: true });
  
      return { chartCanvas, store };
    },
  });
  </script>
  
  <style scoped>
  .section {
    margin-bottom: 40px;
  }
  
  h2 {
    margin-top: 0;
  }
  </style>