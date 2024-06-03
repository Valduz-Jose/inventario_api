from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from .database import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    cantidad = Column(Float, default=0)
    ultimo_movimiento = Column(DateTime, default=func.now())


class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=func.now())
    hora = Column(DateTime, default=func.now())
    cantidad = Column(Float)
    tipo = Column(String)
    producto_id = Column(Integer)
