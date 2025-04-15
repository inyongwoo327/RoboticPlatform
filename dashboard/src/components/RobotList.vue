<template>
    <ul>
      <li v-for="robot in robots" :key="robot.id">
        {{ robot.name }} - {{ robot.status }}
      </li>
    </ul>
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
        required: true,
      },
    },
  });
  </script>
  
  <style scoped>
  ul {
    list-style: none;
    padding: 0;
  }
  
  li {
    padding: 10px 0;
  }
  </style>