import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const warehouseApi = {
  getAll: () => api.get("/warehouses"),
  getById: (id) => api.get(`/warehouses/${id}`),
  create: (data) => api.post("/warehouses", data),
  update: (id, data) => api.put(`/warehouses/${id}`, data),
};

export const agentApi = {
  getAll: () => api.get("/agents"),
  getById: (id) => api.get(`/agents/${id}`),
  create: (data) => api.post("/agents", data),
  update: (id, data) => api.put(`/agents/${id}`, data),
  checkIn: (id) => api.put(`/agents/${id}`, { check_in: true }),
};

export const orderApi = {
  getAll: () => api.get("/orders"),
  getById: (id) => api.get(`/orders/${id}`),
  create: (data) => api.post("/orders", data),
  allocate: (warehouseId) => api.post("/allocate-orders", { warehouse_id: warehouseId }),
}; 