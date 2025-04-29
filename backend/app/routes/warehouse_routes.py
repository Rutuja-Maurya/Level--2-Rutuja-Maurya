import falcon
from ..models.models import Warehouse
from ..utils.db import get_db
from sqlalchemy.orm import Session

class WarehouseResource:
    def on_get(self, req, resp):
        db = next(get_db())
        warehouses = db.query(Warehouse).all()
        resp.media = [{
            'id': w.id,
            'name': w.name,
            'address': w.address,
            'latitude': w.latitude,
            'longitude': w.longitude,
            'capacity': w.capacity
        } for w in warehouses]
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        db = next(get_db())
        data = req.media
        
        warehouse = Warehouse(
            name=data['name'],
            address=data['address'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            capacity=data['capacity']
        )
        
        db.add(warehouse)
        db.commit()
        db.refresh(warehouse)
        
        resp.media = {
            'id': warehouse.id,
            'name': warehouse.name,
            'address': warehouse.address,
            'latitude': warehouse.latitude,
            'longitude': warehouse.longitude,
            'capacity': warehouse.capacity
        }
        resp.status = falcon.HTTP_201

class WarehouseDetailResource:
    def on_get(self, req, resp, warehouse_id):
        db = next(get_db())
        warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        
        if not warehouse:
            resp.status = falcon.HTTP_404
            return
        
        resp.media = {
            'id': warehouse.id,
            'name': warehouse.name,
            'address': warehouse.address,
            'latitude': warehouse.latitude,
            'longitude': warehouse.longitude,
            'capacity': warehouse.capacity
        }
        resp.status = falcon.HTTP_200 