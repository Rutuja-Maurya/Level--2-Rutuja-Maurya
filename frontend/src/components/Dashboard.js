import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState({
    total_orders: 0,
    pending_orders: 0,
    assigned_orders: 0,
    delivered_orders: 0,
    postponed_orders: 0,
    active_agents: 0,
    agents_with_orders: 0,
    efficiency_metrics: {
      avg_orders_per_agent: 0,
      agents_at_capacity: 0,
      agents_above_25_orders: 0
    }
  });
  const [warehouses, setWarehouses] = useState([]);
  const [isAllocating, setIsAllocating] = useState(false);
  const [lastAllocationMessage, setLastAllocationMessage] = useState('');

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/allocation-status');
      const data = {
        ...response.data,
        efficiency_metrics: response.data.efficiency_metrics || {
          avg_orders_per_agent: 0,
          agents_at_capacity: 0,
          agents_above_25_orders: 0
        }
      };
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchWarehouses = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/warehouses');
      setWarehouses(response.data);
    } catch (error) {
      console.error('Error fetching warehouses:', error);
    }
  };

  const triggerAllocation = async () => {
    setIsAllocating(true);
    try {
      const response = await axios.post('http://localhost:8000/api/allocate-orders');
      setLastAllocationMessage(response.data.message);
      await fetchStats();
    } catch (error) {
      setLastAllocationMessage(error.response?.data?.error || 'Error triggering allocation');
      console.error('Error triggering allocation:', error);
    } finally {
      setIsAllocating(false);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchWarehouses();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">
      <h1>Delivery System Dashboard</h1>
      
      {lastAllocationMessage && (
        <div className={`allocation-message ${lastAllocationMessage.includes('Error') ? 'error' : 'success'}`}>
          {lastAllocationMessage}
        </div>
      )}
      
      {/* Payment Structure Section */}
      <div className="payment-structure">
        <h2>Payment Structure</h2>
        <div className="payment-cards">
          <div className="stat-card">
            <h3>Base Pay</h3>
            <p>₹500</p>
            <span className="payment-note">For showing up</span>
          </div>
          <div className="stat-card">
            <h3>25+ Orders</h3>
            <p>₹35</p>
            <span className="payment-note">Per order</span>
          </div>
          <div className="stat-card">
            <h3>50+ Orders</h3>
            <p>₹42</p>
            <span className="payment-note">Per order</span>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-container">
        <div className="stat-card">
          <h3>Total Orders</h3>
          <p>{stats.total_orders}</p>
        </div>
        <div className="stat-card">
          <h3>Pending Orders</h3>
          <p>{stats.pending_orders}</p>
        </div>
        <div className="stat-card">
          <h3>Assigned Orders</h3>
          <p>{stats.assigned_orders}</p>
        </div>
        <div className="stat-card">
          <h3>Delivered Orders</h3>
          <p>{stats.delivered_orders}</p>
        </div>
        <div className="stat-card highlight">
          <h3>Postponed Orders</h3>
          <p>{stats.postponed_orders}</p>
        </div>
      </div>

      {/* Efficiency Metrics */}
      <div className="efficiency-metrics">
        <h2>Efficiency Metrics</h2>
        <div className="metrics-grid">
          <div className="stat-card">
            <h3>Avg Orders/Agent</h3>
            <p>{stats.efficiency_metrics.avg_orders_per_agent}</p>
          </div>
          <div className="stat-card">
            <h3>Agents at Capacity (50+)</h3>
            <p>{stats.efficiency_metrics.agents_at_capacity}</p>
          </div>
          <div className="stat-card">
            <h3>Agents Above 25 Orders</h3>
            <p>{stats.efficiency_metrics.agents_above_25_orders}</p>
          </div>
        </div>
      </div>

      {/* Agent Status */}
      <div className="agent-status">
        <h2>Agent Status</h2>
        <div className="agent-stats">
          <div className="stat-card">
            <h3>Active Agents</h3>
            <p>{stats.active_agents}</p>
          </div>
          <div className="stat-card">
            <h3>Agents with Orders</h3>
            <p>{stats.agents_with_orders}</p>
          </div>
        </div>
      </div>

      {/* Allocation Controls */}
      <div className="allocation-controls">
        <button 
          onClick={triggerAllocation} 
          disabled={isAllocating}
          className="allocation-button"
        >
          {isAllocating ? 'Allocating...' : 'Trigger Order Allocation'}
        </button>
        <p className="allocation-note">
          Note: Allocation runs automatically at 9 AM. Manual trigger available for testing.
        </p>
      </div>

      {/* Warehouse List */}
      <div className="warehouse-list">
        <h2>Warehouses</h2>
        <div className="warehouse-grid">
          {warehouses.map(warehouse => (
            <div key={warehouse.id} className="warehouse-card">
              <h3>{warehouse.name}</h3>
              <p>Address: {warehouse.address}</p>
              <p>Capacity: {warehouse.capacity}</p>
              <p>Active Agents: {warehouse.active_agents}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 