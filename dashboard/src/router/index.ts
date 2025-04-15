import { createRouter, createWebHistory } from 'vue-router';
import RobotsView from '../views/RobotsView.vue';
import MetricsView from '../views/MetricsView.vue';
import LogsView from '../views/LogsView.vue';

const routes = [
  {
    path: '/robots',
    name: 'Robots',
    component: RobotsView,
  },
  {
    path: '/metrics',
    name: 'Metrics',
    component: MetricsView,
  },
  {
    path: '/logs',
    name: 'Logs',
    component: LogsView,
  },
  {
    path: '/',
    redirect: '/robots',
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;