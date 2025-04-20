<!-- src/components/RobotList.vue -->
<template>
  <div class="robot-list">
    <table v-if="robots.length > 0">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="robot in robots" :key="robot.id">
          <td>{{ robot.id }}</td>
          <td>{{ robot.name }}</td>
          <td>
            <span :class="['status', robot.status.toLowerCase()]">
              {{ robot.status }}
            </span>
          </td>
          <td>
            <button @click="$emit('statusChange', robot.id)" class="action-button">
              {{ robot.status === 'online' ? 'Set Offline' : 'Set Online' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="no-data">
      No robots found
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

interface Robot {
  id: string;
  name: string;
  status: string;
}

export default defineComponent({
  name: 'RobotList',
  props: {
    robots: {
      type: Array as PropType<Robot[]>,
      required: true
    }
  },
  emits: ['statusChange']
});
</script>

<style scoped>
.robot-list {
  width: 100%;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
  font-weight: bold;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9em;
}

.status.online {
  background-color: #d4edda;
  color: #155724;
}

.status.offline {
  background-color: #f8d7da;
  color: #721c24;
}

.status.maintenance {
  background-color: #fff3cd;
  color: #856404;
}

.action-button {
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
}

.action-button:hover {
  background-color: #0069d9;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #6c757d;
  font-style: italic;
  background-color: #f8f9fa;
  border-radius: 4px;
}
</style>