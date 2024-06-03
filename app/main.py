from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/productos/", response_model=schemas.Producto)
def create_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    db_producto = models.Producto(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


@app.post("/movimientos/entrada/", response_model=schemas.Movimiento)
def create_movimiento_entrada(movimiento: schemas.MovimientoCreate, db: Session = Depends(get_db)):
    db_movimiento = models.Movimiento(**movimiento.dict())
    db.add(db_movimiento)
    producto = db.query(models.Producto).filter(
        models.Producto.id == movimiento.producto_id).first()
    if producto:
        producto.cantidad += movimiento.cantidad
        producto.ultimo_movimiento = db_movimiento.fecha
    db.commit()
    db.refresh(db_movimiento)
    return db_movimiento


@app.post("/movimientos/entrada/sql/", response_model=schemas.Movimiento)
def create_movimiento_entrada_sql(movimiento: schemas.MovimientoCreate, db: Session = Depends(get_db)):
    sql = "INSERT INTO movimientos (fecha, hora, cantidad, tipo, producto_id) VALUES (:fecha, :hora, :cantidad, :tipo, :producto_id)"
    db.execute(sql, {'fecha': movimiento.fecha, 'hora': movimiento.hora,
               'cantidad': movimiento.cantidad, 'tipo': movimiento.tipo, 'producto_id': movimiento.producto_id})
    producto = db.query(models.Producto).filter(
        models.Producto.id == movimiento.producto_id).first()
    if producto:
        producto.cantidad += movimiento.cantidad
        producto.ultimo_movimiento = movimiento.fecha
    db.commit()
    return movimiento


@app.post("/movimientos/salida/", response_model=schemas.Movimiento)
def create_movimiento_salida(movimiento: schemas.MovimientoCreate, db: Session = Depends(get_db)):
    db_movimiento = models.Movimiento(**movimiento.dict())
    db.add(db_movimiento)
    producto = db.query(models.Producto).filter(
        models.Producto.id == movimiento.producto_id).first()
    if producto:
        producto.cantidad -= movimiento.cantidad
        producto.ultimo_movimiento = db_movimiento.fecha
    db.commit()
    db.refresh(db_movimiento)
    return db_movimiento


@app.post("/movimientos/salida/sql/", response_model=schemas.Movimiento)
def create_movimiento_salida_sql(movimiento: schemas.MovimientoCreate, db: Session = Depends(get_db)):
    sql = "INSERT INTO movimientos (fecha, hora, cantidad, tipo, producto_id) VALUES (:fecha, :hora, :cantidad, :tipo, :producto_id)"
    db.execute(sql, {'fecha': movimiento.fecha, 'hora': movimiento.hora,
               'cantidad': movimiento.cantidad, 'tipo': movimiento.tipo, 'producto_id': movimiento.producto_id})
    producto = db.query(models.Producto).filter(
        models.Producto.id == movimiento.producto_id).first()
    if producto:
        producto.cantidad -= movimiento.cantidad
        producto.ultimo_movimiento = movimiento.fecha
    db.commit()
    return movimiento


@app.get("/productos/{producto_id}", response_model=schemas.Producto)
def read_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(
        models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto not found")
    return producto


@app.get("/productos/{producto_id}/movimientos/", response_model=schemas.Producto)
def read_producto_movimientos(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(
        models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto not found")
    movimientos = db.query(models.Movimiento).filter(
        models.Movimiento.producto_id == producto_id).all()
    return {"producto": producto, "movimientos": movimientos}
