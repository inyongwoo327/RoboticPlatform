<template>
    <div class="section">
      <h2>Robots</h2>
      <RobotList :robots="store.robots" />
      <AddRobot />
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  import RobotList from '../components/RobotList.vue';
  import AddRobot from '../components/AddRobot.vue';
  import { useRobotStore } from '../stores/robotStore'
  
  export default defineComponent({
    name: 'RobotsView',
    components: { RobotList, AddRobot },
    setup() {
      const store = useRobotStore();
      store.fetchRobots();
      return { store };
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