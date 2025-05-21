<template>
  <div class="section">
    <h2>Logs</h2>
    
    <div class="search-controls">
      <input v-model="filter.level" placeholder="Filter by level..." @input="updateFilter" />
      <input v-model="filter.timestamp" placeholder="Filter by timestamp..." @input="updateFilter" />
    </div>
    
    <ul class="logs-list">
      <li v-for="(log, index) in store.filteredLogs" :key="index" :class="'level-' + log.level">
        {{ log.timestamp }} [{{ log.level }}] {{ log.message }}
      </li>
      <li v-if="store.filteredLogs.length === 0" class="no-logs">
        No logs available
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useLogStore } from '../stores/logStore';

export default defineComponent({
  name: 'LogsView',
  setup() {
    const store = useLogStore();
    const filter = ref({ level: '', timestamp: '' });
    
    const updateFilter = () => {
      store.updateLogFilter(filter.value);
    };
    
    store.fetchLogs();
    
    return { store, filter, updateFilter };
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

.search-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

input {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
  flex-grow: 1;
}

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