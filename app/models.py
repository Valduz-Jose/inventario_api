from sqlalchemy import Column, Integer, String, Float, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    cantidad = Column(Float, default=0)
    ultimo_movimiento_id = Column(Integer, ForeignKey("movimientos.id"), nullable=True)

    # Relación con Movimiento para el último movimiento
    ultimo_movimiento = relationship("Movimiento", foreign_keys=[ultimo_movimiento_id], back_populates="producto_ultimo_movimiento")

    # Relación con Movimiento para todos los movimientos
    movimientos = relationship("Movimiento", back_populates="producto", foreign_keys="[Movimiento.producto_id]")

class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, default=datetime.now().date)
    hora = Column(Time, default=datetime.now().time)
    cantidad = Column(Float)
    tipo = Column(String)
    producto_id = Column(Integer, ForeignKey("productos.id"))

    # Relación con Producto para todos los movimientos
    producto = relationship("Producto", back_populates="movimientos", foreign_keys=[producto_id])

    # Relación inversa para el último movimiento del producto
    producto_ultimo_movimiento = relationship("Producto", back_populates="ultimo_movimiento", foreign_keys=[Producto.ultimo_movimiento_id], uselist=False)

# Configurar relaciones inversas correctamente
Producto.movimientos = relationship("Movimiento", back_populates="producto", foreign_keys=[Movimiento.producto_id])
