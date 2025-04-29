from datetime import datetime, timedelta
from ..models.models import Agent, Order, Warehouse
from .db import Session
from ..config import MAX_WORKING_HOURS, MAX_DAILY_DISTANCE, TRAVEL_TIME_PER_KM
from ..config import BASE_PAY, ORDERS_25_PLUS_RATE, ORDERS_50_PLUS_RATE
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def calculate_route_time(distance):
    """Calculate time needed to cover the distance"""
    return (distance * TRAVEL_TIME_PER_KM) / 60  # Convert to hours

def calculate_payment(orders_count):
    """Calculate agent payment based on order count"""
    if orders_count >= 50:
        return BASE_PAY + (orders_count * ORDERS_50_PLUS_RATE)
    elif orders_count >= 25:
        return BASE_PAY + (orders_count * ORDERS_25_PLUS_RATE)
    return BASE_PAY

def is_allocation_time():
    """Check if it's time to allocate orders (X hours in the morning)"""
    now = datetime.utcnow()
    allocation_hour = 9  # Set allocation time to 9 AM
    return now.hour == allocation_hour

def allocate_orders():
    """Main function to allocate orders to agents"""
    # Only allocate at specific time unless forced
    if not is_allocation_time():
        return False, "Not allocation time yet"

    session = Session()
    try:
        # Get all active agents who have checked in today
        today = datetime.utcnow().date()
        agents = session.query(Agent).filter(
            Agent.is_active == True,
            Agent.check_in_time >= today
        ).all()
        
        # Get all pending orders
        pending_orders = session.query(Order).filter(
            Order.status == 'pending'
        ).all()
        
        # Group orders by warehouse
        warehouse_orders = {}
        for order in pending_orders:
            if order.warehouse_id not in warehouse_orders:
                warehouse_orders[order.warehouse_id] = []
            warehouse_orders[order.warehouse_id].append(order)
        
        # Track postponed orders
        postponed_orders = []
        
        # Allocate orders for each warehouse
        for warehouse_id, orders in warehouse_orders.items():
            warehouse = session.query(Warehouse).get(warehouse_id)
            warehouse_agents = [a for a in agents if a.warehouse_id == warehouse_id]
            
            # Sort agents by current load (try to maximize agent utilization)
            warehouse_agents.sort(key=lambda x: x.daily_orders)
            
            # Calculate optimal orders per agent to maximize efficiency
            total_orders = len(orders)
            active_agents = len(warehouse_agents)
            if active_agents > 0:
                target_orders_per_agent = min(50, total_orders // active_agents)
            else:
                continue
            
            # Sort orders by distance from warehouse for efficient routing
            orders.sort(key=lambda x: calculate_distance(
                warehouse.latitude, warehouse.longitude,
                x.latitude, x.longitude
            ))
            
            # Allocate orders to agents
            for agent in warehouse_agents:
                if agent.daily_distance >= MAX_DAILY_DISTANCE:
                    continue
                
                # Calculate remaining working hours
                remaining_hours = MAX_WORKING_HOURS
                if agent.check_in_time:
                    elapsed_hours = (datetime.utcnow() - agent.check_in_time).total_seconds() / 3600
                    remaining_hours -= elapsed_hours
                
                # Try to assign optimal number of orders
                agent_orders = []
                total_distance = agent.daily_distance
                
                for order in orders[:]:
                    if len(agent_orders) >= target_orders_per_agent:
                        break
                        
                    if order.agent_id is not None:
                        continue
                    
                    # Calculate distance for this order
                    distance = calculate_distance(
                        warehouse.latitude, warehouse.longitude,
                        order.latitude, order.longitude
                    )
                    
                    # Check if adding this order would exceed limits
                    new_total_distance = total_distance + distance
                    if (new_total_distance > MAX_DAILY_DISTANCE or
                        calculate_route_time(new_total_distance) > remaining_hours):
                        postponed_orders.append(order)
                        continue
                    
                    # Assign order to agent
                    order.agent_id = agent.id
                    order.status = 'assigned'
                    order.assigned_at = datetime.utcnow()
                    total_distance = new_total_distance
                    agent_orders.append(order)
                    orders.remove(order)
                
                # Update agent metrics
                if agent_orders:
                    agent.daily_orders += len(agent_orders)
                    agent.daily_distance = total_distance
        
        # Mark remaining orders as postponed
        for order in postponed_orders:
            order.status = 'postponed'
        
        session.commit()
        return True, "Orders allocated successfully"
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close() 