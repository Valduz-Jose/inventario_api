from sqlalchemy import Column, Integer, String, DateTime, Float, Date, Time
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime
class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    cantidad = Column(Float, default=0)
    ultimo_movimiento = Column(DateTime, default=datetime.now())


class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, default=datetime.now().date())
    hora = Column(Time, default=datetime.now().time())
    cantidad = Column(Float)
    tipo = Column(String)
    producto_id = Column(Integer)
