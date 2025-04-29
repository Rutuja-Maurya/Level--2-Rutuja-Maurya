import falcon
from ..utils.allocation_service import allocate_orders
from ..utils.db import Session
from ..models.models import Order, Agent

class OrderAllocationResource:
    def on_post(self, req, resp):
        """Trigger order allocation process"""
        try:
            success, message = allocate_orders()
            if success:
                resp.status = falcon.HTTP_200
                resp.media = {"message": message}
            else:
                resp.status = falcon.HTTP_400
                resp.media = {"error": message}
        except Exception as e:
            resp.status = falcon.HTTP_500
            resp.media = {"error": str(e)}

class AllocationStatusResource:
    def on_get(self, req, resp):
        """Get current allocation status"""
        session = Session()
        try:
            # Get allocation statistics
            total_orders = session.query(Order).count()
            pending_orders = session.query(Order).filter(Order.status == 'pending').count()
            assigned_orders = session.query(Order).filter(Order.status == 'assigned').count()
            delivered_orders = session.query(Order).filter(Order.status == 'delivered').count()
            postponed_orders = session.query(Order).filter(Order.status == 'postponed').count()
            
            # Get agent statistics
            active_agents = session.query(Agent).filter(Agent.is_active == True).count()
            agents_with_orders = session.query(Agent).filter(Agent.daily_orders > 0).count()
            
            # Calculate efficiency metrics
            total_active_agents = max(1, active_agents)  # Avoid division by zero
            avg_orders_per_agent = assigned_orders / total_active_agents
            agents_at_capacity = session.query(Agent).filter(Agent.daily_orders >= 50).count()
            agents_above_25 = session.query(Agent).filter(Agent.daily_orders >= 25).count()
            
            resp.media = {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "assigned_orders": assigned_orders,
                "delivered_orders": delivered_orders,
                "postponed_orders": postponed_orders,
                "active_agents": active_agents,
                "agents_with_orders": agents_with_orders,
                "efficiency_metrics": {
                    "avg_orders_per_agent": round(avg_orders_per_agent, 2),
                    "agents_at_capacity": agents_at_capacity,
                    "agents_above_25_orders": agents_above_25
                }
            }
        except Exception as e:
            resp.status = falcon.HTTP_500
            resp.media = {"error": str(e)}
        finally:
            session.close() 