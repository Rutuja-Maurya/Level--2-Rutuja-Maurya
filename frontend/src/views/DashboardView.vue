<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      <!-- Warehouse Stats -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900">Warehouses</h3>
        <p class="mt-2 text-3xl font-semibold text-gray-900">{{ stats.warehouses }}</p>
        <p class="mt-1 text-sm text-gray-500">Total warehouses</p>
      </div>

      <!-- Agent Stats -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900">Active Agents</h3>
        <p class="mt-2 text-3xl font-semibold text-gray-900">{{ stats.activeAgents }}</p>
        <p class="mt-1 text-sm text-gray-500">Agents checked in today</p>
      </div>

      <!-- Order Stats -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900">Pending Orders</h3>
        <p class="mt-2 text-3xl font-semibold text-gray-900">{{ stats.pendingOrders }}</p>
        <p class="mt-1 text-sm text-gray-500">Orders waiting for allocation</p>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="card">
      <h3 class="text-lg font-medium text-gray-900">Recent Activity</h3>
      <div class="mt-4 flow-root">
        <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <table class="min-w-full divide-y divide-gray-300">
              <thead>
                <tr>
                  <th class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900">Time</th>
                  <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Activity</th>
                  <th class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="activity in recentActivity" :key="activity.id">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-500">
                    {{ activity.time }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    {{ activity.description }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm">
                    <span
                      :class="[
                        activity.status === 'success' ? 'text-green-700 bg-green-50' : 'text-yellow-700 bg-yellow-50',
                        'inline-flex rounded-full px-2 text-xs font-semibold leading-5'
                      ]"
                    >
                      {{ activity.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { warehouseApi, agentApi, orderApi } from '../api';

const stats = ref({
  warehouses: 0,
  activeAgents: 0,
  pendingOrders: 0,
});

const recentActivity = ref([]);

const fetchStats = async () => {
  try {
    const [warehouses, agents, orders] = await Promise.all([
      warehouseApi.getAll(),
      agentApi.getAll(),
      orderApi.getAll(),
    ]);

    stats.value = {
      warehouses: warehouses.data.length,
      activeAgents: agents.data.filter(a => a.is_active).length,
      pendingOrders: orders.data.filter(o => o.status === 'pending').length,
    };
  } catch (error) {
    console.error('Error fetching stats:', error);
  }
};

onMounted(() => {
  fetchStats();
});
</script> 