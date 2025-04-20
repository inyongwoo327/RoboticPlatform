<template>
  <ul class="logs-list">
    <li v-for="(log, index) in store.logs" :key="index" :class="'level-' + log.level">
      {{ log.timestamp }} [{{ log.level }}] {{ log.message }}
    </li>
    <li v-if="store.logs.length === 0" class="no-logs">
      No logs available
    </li>
  </ul>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import { useLogStore } from '../stores/logStore';

export default defineComponent({
  name: 'LogsView',
  props: {
    filter: {
      type: Object as PropType<{ level: string; timestamp: string }>,
      default: () => ({ level: '', timestamp: '' })
    }
  },
  setup(props) {
    const store = useLogStore();
    
    // Update filter when props change
    const updateFilter = () => {
      const filterData = {
        level: props.filter.level || '',
        timestamp: props.filter.timestamp || ''
      };
      store.updateLogFilter(filterData);
    };
    
    // Fetch logs when component is mounted
    store.fetchLogs();
    
    return { store, updateFilter };
  }
});
</script>

<style scoped>
.logs-list {
  background-color: #1e1e1e;
  color: #f0f0f0;
  border-radius: 4px;
  list-style: none;
  padding: 0;
  max-height: 400px;
  overflow-y: auto;
  font-family: monospace;
}

.logs-list li {
  padding: 8px 12px;
  border-bottom: 1px solid #333;
  display: flex;
  align-items: center;
}

.logs-list li:hover {
  background-color: #2a2a2a;
}

.level-info {
  border-left: 3px solid #4caf50;
}

.level-warn, .level-warning {
  border-left: 3px solid #ff9800;
  background-color: rgba(255, 152, 0, 0.1);
}

.level-error {
  border-left: 3px solid #f44336;
  background-color: rgba(244, 67, 54, 0.1);
}

.no-logs {
  text-align: center;
  padding: 20px;
  color: #999;
}
</style>