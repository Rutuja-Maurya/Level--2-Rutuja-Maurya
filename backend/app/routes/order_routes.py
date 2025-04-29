import falcon
from datetime import datetime
from ..models.models import Order, Agent, Warehouse
from ..utils.db import get_db
from sqlalchemy.orm import Session
from ..config import MAX_WORKING_HOURS, MAX_DAILY_DISTANCE, TRAVEL_TIME_PER_KM
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula to calculate distance between two points
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

class OrderResource:
    def on_get(self, req, resp):
        db = next(get_db())
        orders = db.query(Order).all()
        resp.media = [{
            'id': o.id,
            'tracking_number': o.tracking_number,
            'warehouse_id': o.warehouse_id,
            'agent_id': o.agent_id,
            'delivery_address': o.delivery_address,
            'latitude': o.latitude,
            'longitude': o.longitude,
            'status': o.status,
            'created_at': o.created_at.isoformat(),
            'assigned_at': o.assigned_at.isoformat() if o.assigned_at else None,
            'delivered_at': o.delivered_at.isoformat() if o.delivered_at else None
        } for o in orders]
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        db = next(get_db())
        data = req.media
        
        order = Order(
            tracking_number=data['tracking_number'],
            warehouse_id=data['warehouse_id'],
            delivery_address=data['delivery_address'],
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        resp.media = {
            'id': order.id,
            'tracking_number': order.tracking_number,
            'warehouse_id': order.warehouse_id,
            'agent_id': order.agent_id,
            'delivery_address': order.delivery_address,
            'latitude': order.latitude,
            'longitude': order.longitude,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'assigned_at': order.assigned_at.isoformat() if order.assigned_at else None,
            'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None
        }
        resp.status = falcon.HTTP_201

class OrderDetailResource:
    def on_get(self, req, resp, order_id):
        db = next(get_db())
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            resp.status = falcon.HTTP_404
            return
        
        resp.media = {
            'id': order.id,
            'tracking_number': order.tracking_number,
            'warehouse_id': order.warehouse_id,
            'agent_id': order.agent_id,
            'delivery_address': order.delivery_address,
            'latitude': order.latitude,
            'longitude': order.longitude,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'assigned_at': order.assigned_at.isoformat() if order.assigned_at else None,
            'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None
        }
        resp.status = falcon.HTTP_200

class OrderAllocationResource:
    def on_post(self, req, resp):
        db = next(get_db())
        data = req.media
        warehouse_id = data.get('warehouse_id')
        
        # Get all active agents at the warehouse
        agents = db.query(Agent).filter(
            Agent.warehouse_id == warehouse_id,
            Agent.is_active == True,
            Agent.check_in_time != None
        ).all()
        
        # Get all pending orders at the warehouse
        orders = db.query(Order).filter(
            Order.warehouse_id == warehouse_id,
            Order.status == 'pending'
        ).all()
        
        # Get warehouse location
        warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        
        # Allocate orders to agents
        for order in orders:
            best_agent = None
            min_additional_distance = float('inf')
            
            for agent in agents:
                # Check if agent can take more orders
                if agent.daily_orders >= 60:  # Maximum orders per day
                    continue
                
                # Calculate additional distance for this order
                if agent.orders:
                    last_order = agent.orders[-1]
                    additional_distance = calculate_distance(
                        last_order.latitude, last_order.longitude,
                        order.latitude, order.longitude
                    )
                else:
                    additional_distance = calculate_distance(
                        warehouse.latitude, warehouse.longitude,
                        order.latitude, order.longitude
                    )
                
                # Check if adding this order would exceed daily distance limit
                if agent.daily_distance + additional_distance > MAX_DAILY_DISTANCE:
                    continue
                
                # Check if adding this order would exceed working hours
                additional_time = (additional_distance * TRAVEL_TIME_PER_KM) / 60  # Convert to hours
                if additional_time > MAX_WORKING_HOURS:
                    continue
                
                if additional_distance < min_additional_distance:
                    min_additional_distance = additional_distance
                    best_agent = agent
            
            if best_agent:
                # Assign order to agent
                order.agent_id = best_agent.id
                order.status = 'assigned'
                order.assigned_at = datetime.utcnow()
                
                # Update agent's daily metrics
                best_agent.daily_orders += 1
                best_agent.daily_distance += min_additional_distance
        
        db.commit()
        
        resp.media = {
            'message': 'Orders allocated successfully',
            'allocated_orders': len([o for o in orders if o.agent_id is not None])
        }
        resp.status = falcon.HTTP_200 