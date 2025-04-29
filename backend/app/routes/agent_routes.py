import falcon
from datetime import datetime
from ..models.models import Agent
from ..utils.db import get_db, Session

class AgentResource:
    def on_get(self, req, resp):
        """Get all agents"""
        session = Session()
        try:
            agents = session.query(Agent).all()
            resp.media = [{
                "id": agent.id,
                "name": agent.name,
                "phone": agent.phone,
                "warehouse_id": agent.warehouse_id,
                "is_active": agent.is_active,
                "daily_distance": agent.daily_distance,
                "daily_orders": agent.daily_orders,
                "check_in_time": agent.check_in_time.isoformat() if agent.check_in_time else None
            } for agent in agents]
        except Exception as e:
            resp.status = falcon.HTTP_500
            resp.media = {"error": str(e)}
        finally:
            session.close()

    def on_post(self, req, resp):
        db = next(get_db())
        data = req.media
        
        agent = Agent(
            name=data['name'],
            phone=data['phone'],
            warehouse_id=data['warehouse_id']
        )
        
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        resp.media = {
            'id': agent.id,
            'name': agent.name,
            'phone': agent.phone,
            'warehouse_id': agent.warehouse_id,
            'is_active': agent.is_active,
            'daily_distance': agent.daily_distance,
            'daily_orders': agent.daily_orders,
            'check_in_time': agent.check_in_time.isoformat() if agent.check_in_time else None
        }
        resp.status = falcon.HTTP_201

class AgentDetailResource:
    def on_get(self, req, resp, agent_id):
        """Get agent details"""
        session = Session()
        try:
            agent = session.query(Agent).get(agent_id)
            if not agent:
                resp.status = falcon.HTTP_404
                resp.media = {"error": "Agent not found"}
                return

            # Calculate earnings
            base_pay = 500  # Minimum guarantee
            per_order_rate = 42 if agent.daily_orders >= 50 else (35 if agent.daily_orders >= 25 else 0)
            total_pay = base_pay + (per_order_rate * agent.daily_orders if per_order_rate > 0 else 0)

            resp.media = {
                "id": agent.id,
                "name": agent.name,
                "phone": agent.phone,
                "warehouse_id": agent.warehouse_id,
                "is_active": agent.is_active,
                "daily_distance": agent.daily_distance,
                "daily_orders": agent.daily_orders,
                "check_in_time": agent.check_in_time.isoformat() if agent.check_in_time else None,
                "earnings": {
                    "base_pay": base_pay,
                    "per_order_rate": per_order_rate,
                    "total_pay": total_pay
                }
            }
        except Exception as e:
            resp.status = falcon.HTTP_500
            resp.media = {"error": str(e)}
        finally:
            session.close()

    def on_put(self, req, resp, agent_id):
        db = next(get_db())
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        
        if not agent:
            resp.status = falcon.HTTP_404
            return
        
        data = req.media
        
        if 'check_in' in data and data['check_in']:
            agent.check_in_time = datetime.utcnow()
            agent.daily_distance = 0
            agent.daily_orders = 0
        
        if 'name' in data:
            agent.name = data['name']
        if 'phone' in data:
            agent.phone = data['phone']
        if 'warehouse_id' in data:
            agent.warehouse_id = data['warehouse_id']
        if 'is_active' in data:
            agent.is_active = data['is_active']
        
        db.commit()
        db.refresh(agent)
        
        resp.media = {
            'id': agent.id,
            'name': agent.name,
            'phone': agent.phone,
            'warehouse_id': agent.warehouse_id,
            'is_active': agent.is_active,
            'daily_distance': agent.daily_distance,
            'daily_orders': agent.daily_orders,
            'check_in_time': agent.check_in_time.isoformat() if agent.check_in_time else None
        }
        resp.status = falcon.HTTP_200 

class AgentCheckInResource:
    def on_post(self, req, resp, agent_id):
        """Handle agent check-in"""
        session = Session()
        try:
            agent = session.query(Agent).get(agent_id)
            if not agent:
                resp.status = falcon.HTTP_404
                resp.media = {"error": "Agent not found"}
                return

            # Reset daily metrics on check-in
            agent.is_active = True
            agent.daily_distance = 0
            agent.daily_orders = 0
            agent.check_in_time = datetime.utcnow()
            
            session.commit()
            resp.status = falcon.HTTP_200
            resp.media = {
                "message": f"Agent {agent.name} checked in successfully",
                "check_in_time": agent.check_in_time.isoformat()
            }
        except Exception as e:
            session.rollback()
            resp.status = falcon.HTTP_500
            resp.media = {"error": str(e)}
        finally:
            session.close() 