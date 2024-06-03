from datetime import datetime
from pydantic import BaseModel


class ProductoBase(BaseModel):
    nombre: str


class ProductoCreate(ProductoBase):
    pass


class Producto(ProductoBase):
    id: int
    cantidad: float
    ultimo_movimiento: datetime

    class Config:
        orm_mode = True


class MovimientoBase(BaseModel):
    cantidad: float
    tipo: str
    producto_id: int


class MovimientoCreate(MovimientoBase):
    pass


class Movimiento(MovimientoBase):
    id: int
    fecha: datetime
    hora: datetime

    class Config:
        orm_mode = True
