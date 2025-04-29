import falcon
from .models.models import Base
from .utils.db import engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Create Falcon application
app = falcon.App(
    cors_enable=True
)

# Import and register routes
from .routes import warehouse_routes, agent_routes, order_routes, allocation_routes

# Register routes
app.add_route('/api/warehouses', warehouse_routes.WarehouseResource())
app.add_route('/api/warehouses/{warehouse_id}', warehouse_routes.WarehouseDetailResource())
app.add_route('/api/agents', agent_routes.AgentResource())
app.add_route('/api/agents/{agent_id}', agent_routes.AgentDetailResource())
app.add_route('/api/orders', order_routes.OrderResource())
app.add_route('/api/orders/{order_id}', order_routes.OrderDetailResource())
app.add_route('/api/allocate-orders', allocation_routes.OrderAllocationResource())
app.add_route('/api/allocation-status', allocation_routes.AllocationStatusResource()) 