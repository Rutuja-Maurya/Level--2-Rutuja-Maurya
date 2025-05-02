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
    """
    Optimized order allocation function that efficiently assigns orders to agents.
    Uses sorting and data structures to avoid nested loops and improve performance.
    """
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
        
        # Create a dictionary to store agent metrics for quick access
        agent_metrics = {
            agent.id: {
                'agent': agent,
                'current_distance': agent.daily_distance,
                'current_orders': agent.daily_orders,
                'remaining_hours': MAX_WORKING_HOURS - (
                    (datetime.utcnow() - agent.check_in_time).total_seconds() / 3600
                    if agent.check_in_time else 0
                )
            }
            for agent in agents
        }
        
        # Group orders by warehouse and sort by distance
        warehouse_orders = {}
        for order in pending_orders:
            if order.warehouse_id not in warehouse_orders:
                warehouse_orders[order.warehouse_id] = []
            warehouse_orders[order.warehouse_id].append(order)
        
        # Process each warehouse's orders
        for warehouse_id, orders in warehouse_orders.items():
            warehouse = session.query(Warehouse).get(warehouse_id)
            if not warehouse:
                continue
                
            # Get agents for this warehouse
            warehouse_agent_ids = [
                agent_id for agent_id, metrics in agent_metrics.items()
                if metrics['agent'].warehouse_id == warehouse_id
            ]
            
            if not warehouse_agent_ids:
                continue
            
            # Sort orders by distance from warehouse for efficient routing
            orders.sort(key=lambda x: calculate_distance(
                warehouse.latitude, warehouse.longitude,
                x.latitude, x.longitude
            ))
            
            # Calculate target orders per agent
            target_orders = min(50, len(orders) // len(warehouse_agent_ids))
            
            # Create a priority queue of agents based on current load
            agent_queue = sorted(
                warehouse_agent_ids,
                key=lambda x: (
                    agent_metrics[x]['current_orders'],
                    agent_metrics[x]['current_distance']
                )
            )
            
            # Process orders in batches for each agent
            for order in orders:
                if order.agent_id is not None:
                    continue
                    
                assigned = False
                # Try to assign order to the least loaded agent
                for agent_id in agent_queue:
                    metrics = agent_metrics[agent_id]
                    
                    # Skip if agent is at capacity
                    if (metrics['current_orders'] >= target_orders or
                        metrics['current_distance'] >= MAX_DAILY_DISTANCE):
                        continue
                    
                    # Calculate distance for this order
                    distance = calculate_distance(
                        warehouse.latitude, warehouse.longitude,
                        order.latitude, order.longitude
                    )
                    
                    # Check if adding this order would exceed limits
                    if (metrics['current_distance'] + distance > MAX_DAILY_DISTANCE or
                        calculate_route_time(metrics['current_distance'] + distance) > metrics['remaining_hours']):
                        continue
                    
                    # Assign order to agent
                    order.agent_id = agent_id
                    order.status = 'assigned'
                    order.assigned_at = datetime.utcnow()
                    
                    # Update agent metrics
                    metrics['current_distance'] += distance
                    metrics['current_orders'] += 1
                    assigned = True
                    break
                
                if not assigned:
                    order.status = 'postponed'
            
            # Update agent records with new metrics
            for agent_id, metrics in agent_metrics.items():
                if agent_id in warehouse_agent_ids:
                    agent = metrics['agent']
                    agent.daily_orders = metrics['current_orders']
                    agent.daily_distance = metrics['current_distance']
        
        session.commit()
        return True, "Orders allocated successfully"
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close() 