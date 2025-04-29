import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/warehouses',
      name: 'warehouses',
      component: () => import('../views/WarehousesView.vue')
    },
    {
      path: '/agents',
      name: 'agents',
      component: () => import('../views/AgentsView.vue')
    },
    {
      path: '/orders',
      name: 'orders',
      component: () => import('../views/OrdersView.vue')
    }
  ]
});

export default router; 