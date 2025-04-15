<template>
    <div class="section">
      <h2>Logs</h2>
      <input v-model="filter.level" placeholder="Filter by level" @input="updateFilter" />
      <input v-model="filter.timestamp" placeholder="Filter by timestamp" @input="updateFilter" />
      <ul>
        <li v-for="(log, index) in store.logs" :key="index">
          {{ log.timestamp }} [{{ log.level }}] {{ log.message }}
        </li>
      </ul>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref } from 'vue';
  import { useDashboardStore } from '../stores/dashboard';
  
  export default defineComponent({
    name: 'LogsView',
    setup() {
      const store = useDashboardStore();
      const filter = ref({ level: '', timestamp: '' });
  
      const updateFilter = () => {
        store.updateLogFilter({ ...filter.value });
      };
  
      store.fetchLogs();
  
      return { store, filter, updateFilter };
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
  
  input {
    margin: 5px;
    padding: 8px;
  }
  
  ul {
    list-style: none;
    padding: 0;
  }
  
  li {
    padding: 10px 0;
  }
  </style>