<template>
  <div class="dashboard">
    <h1>Delivery System Dashboard</h1>
    
    <!-- Statistics Cards -->
    <div class="stats-container">
      <div class="stat-card">
        <h3>Total Orders</h3>
        <p>{{ stats.total_orders }}</p>
      </div>
      <div class="stat-card">
        <h3>Pending Orders</h3>
        <p>{{ stats.pending_orders }}</p>
      </div>
      <div class="stat-card">
        <h3>Assigned Orders</h3>
        <p>{{ stats.assigned_orders }}</p>
      </div>
      <div class="stat-card">
        <h3>Delivered Orders</h3>
        <p>{{ stats.delivered_orders }}</p>
      </div>
    </div>

    <!-- Agent Status -->
    <div class="agent-status">
      <h2>Agent Status</h2>
      <div class="agent-stats">
        <div class="stat-card">
          <h3>Active Agents</h3>
          <p>{{ stats.active_agents }}</p>
        </div>
        <div class="stat-card">
          <h3>Agents with Orders</h3>
          <p>{{ stats.agents_with_orders }}</p>
        </div>
      </div>
    </div>

    <!-- Allocation Controls -->
    <div class="allocation-controls">
      <button @click="triggerAllocation" :disabled="isAllocating">
        {{ isAllocating ? 'Allocating...' : 'Trigger Order Allocation' }}
      </button>
    </div>

    <!-- Warehouse List -->
    <div class="warehouse-list">
      <h2>Warehouses</h2>
      <div v-for="warehouse in warehouses" :key="warehouse.id" class="warehouse-card">
        <h3>{{ warehouse.name }}</h3>
        <p>Address: {{ warehouse.address }}</p>
        <p>Capacity: {{ warehouse.capacity }}</p>
        <p>Active Agents: {{ warehouse.active_agents }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        total_orders: 0,
        pending_orders: 0,
        assigned_orders: 0,
        delivered_orders: 0,
        active_agents: 0,
        agents_with_orders: 0
      },
      warehouses: [],
      isAllocating: false
    };
  },
  methods: {
    async fetchStats() {
      try {
        const response = await axios.get('http://localhost:8000/api/allocation-status');
        this.stats = response.data;
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    },
    async fetchWarehouses() {
      try {
        const response = await axios.get('http://localhost:8000/api/warehouses');
        this.warehouses = response.data;
      } catch (error) {
        console.error('Error fetching warehouses:', error);
      }
    },
    async triggerAllocation() {
      this.isAllocating = true;
      try {
        await axios.post('http://localhost:8000/api/allocate-orders');
        await this.fetchStats();
      } catch (error) {
        console.error('Error triggering allocation:', error);
      } finally {
        this.isAllocating = false;
      }
    }
  },
  mounted() {
    this.fetchStats();
    this.fetchWarehouses();
    // Refresh stats every 30 seconds
    setInterval(this.fetchStats, 30000);
  }
};
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-card h3 {
  margin: 0;
  color: #666;
  font-size: 1rem;
}

.stat-card p {
  margin: 10px 0 0;
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

.agent-status {
  margin-bottom: 30px;
}

.agent-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.allocation-controls {
  margin-bottom: 30px;
}

button {
  background: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.warehouse-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.warehouse-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.warehouse-card h3 {
  margin: 0;
  color: #2c3e50;
}

.warehouse-card p {
  margin: 10px 0;
  color: #666;
}
</style> 