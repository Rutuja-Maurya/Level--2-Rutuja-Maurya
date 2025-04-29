from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Warehouse(Base):
    __tablename__ = 'warehouses'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agents = relationship("Agent", back_populates="warehouse")
    orders = relationship("Order", back_populates="warehouse")

class Agent(Base):
    __tablename__ = 'agents'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    is_active = Column(Boolean, default=True)
    daily_distance = Column(Float, default=0.0)  # in kilometers
    daily_orders = Column(Integer, default=0)
    check_in_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    warehouse = relationship("Warehouse", back_populates="agents")
    orders = relationship("Order", back_populates="agent")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    tracking_number = Column(String(50), unique=True, nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    agent_id = Column(Integer, ForeignKey('agents.id'), nullable=True)
    delivery_address = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(20), default='pending')  # pending, assigned, delivered
    created_at = Column(DateTime, default=datetime.utcnow)
    assigned_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    warehouse = relationship("Warehouse", back_populates="orders")
    agent = relationship("Agent", back_populates="orders") 