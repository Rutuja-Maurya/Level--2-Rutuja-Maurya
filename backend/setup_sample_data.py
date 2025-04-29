import os
import sys
from datetime import datetime, timedelta
import random

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.models.models import Warehouse, Agent, Order
from backend.app.utils.db import Session

def create_sample_data():
    session = Session()
    try:
        # Create 10 warehouses
        warehouses = []
        for i in range(10):
            warehouse = Warehouse(
                name=f"Warehouse {i+1}",
                address=f"Address {i+1}, City",
                latitude=random.uniform(12.9, 13.1),  # Example coordinates for a city
                longitude=random.uniform(77.5, 77.7),
                capacity=100
            )
            session.add(warehouse)
            warehouses.append(warehouse)
        
        session.commit()
        
        # Create 20 agents per warehouse
        agents = []
        for warehouse in warehouses:
            for j in range(20):
                agent = Agent(
                    name=f"Agent {len(agents)+1}",
                    phone=f"+91{random.randint(1000000000, 9999999999)}",
                    warehouse_id=warehouse.id,
                    is_active=True,
                    check_in_time=datetime.utcnow()
                )
                session.add(agent)
                agents.append(agent)
        
        session.commit()
        
        # Create 60 orders per warehouse
        for warehouse in warehouses:
            for k in range(60):
                order = Order(
                    tracking_number=f"ORD{random.randint(100000, 999999)}",
                    warehouse_id=warehouse.id,
                    delivery_address=f"Delivery Address {k+1}, City",
                    latitude=random.uniform(12.9, 13.1),
                    longitude=random.uniform(77.5, 77.7),
                    status='pending'
                )
                session.add(order)
        
        session.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error creating sample data: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    create_sample_data() 