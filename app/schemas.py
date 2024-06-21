from datetime import date, time
from pydantic import BaseModel
from typing import Optional


class MovimientoBase(BaseModel):
    cantidad: float
    producto_id: int


class MovimientoCreate(MovimientoBase):
    pass


class Movimiento(MovimientoBase):
    id: int
    fecha: date
    hora: time
    tipo: str

    class Config:
        from_attributes = True

class ProductoBase(BaseModel):
    nombre: str


class ProductoCreate(ProductoBase):
    pass


class Producto(ProductoBase):
    id: int
    cantidad: float
    ultimo_movimiento_id: Optional[int|Movimiento]

    class Config:
        from_attributes = True