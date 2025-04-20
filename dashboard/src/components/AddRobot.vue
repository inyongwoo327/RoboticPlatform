<template>
    <div>
      <h3>Add Robot</h3>
      <input v-model="robot.id" placeholder="ID" />
      <input v-model="robot.name" placeholder="Name" />
      <select v-model="robot.status">
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
      <button @click="addRobot">Add</button>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref } from 'vue';
  import { useRobotStore } from '../stores/robotStore'
  
  interface Robot {
    id: string;
    name: string;
    status: string;
  }
  
  export default defineComponent({
    name: 'AddRobot',
    setup() {
      const store = useRobotStore();
      const robot = ref<Robot>({ id: '', name: '', status: 'active' });
  
      const addRobot = () => {
        if (robot.value.id && robot.value.name) {
          store.addRobot({ ...robot.value });
          robot.value = { id: '', name: '', status: 'active' };
        }
      };
  
      return { robot, addRobot };
    },
  });
  </script>
  
  <style scoped>
  input,
  select,
  button {
    margin: 5px;
    padding: 8px;
  }
  
  button {
    cursor: pointer;
    background-color: #8884d8;
    color: white;
    border: none;
    border-radius: 4px;
  }
  
  button:hover {
    background-color: #6a67b5;
  }
  </style>