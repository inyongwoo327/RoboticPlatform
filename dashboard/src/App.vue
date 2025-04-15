<template>
  <div class="container">
    <h1>Robotics Dashboard</h1>
    <nav>
      <router-link to="/robots">Robots</router-link> |
      <router-link to="/metrics">Metrics</router-link> |
      <router-link to="/logs">Logs</router-link>
    </nav>
    <router-view />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'App',
});
</script>

<style scoped>
.container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
}

nav {
  margin-bottom: 20px;
}

nav a {
  margin: 0 10px;
  text-decoration: none;
  color: #8884d8;
}

nav a:hover {
  color: #6a67b5;
}
</style>