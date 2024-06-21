from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database
from datetime import datetime
from sqlalchemy import text

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
    fecha_actual = datetime.now()
    db_movimiento = models.Movimiento(
        fecha=fecha_actual.date(),
        hora=fecha_actual.time(),
        cantidad=movimiento.cantidad,
        tipo="Salida",
        producto_id=movimiento.producto_id
    )
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
    fecha_actual = datetime.now()
    sql = text("INSERT INTO movimientos (fecha, hora, cantidad, tipo, producto_id) VALUES (:fecha, :hora, :cantidad, :tipo, :producto_id)")
    db.execute(sql, {'fecha': fecha_actual.date().isoformat(), 'hora':fecha_actual.time().isoformat() ,'cantidad': movimiento.cantidad, 'tipo': "Entrada", 'producto_id': movimiento.producto_id})
    
    producto = db.query(models.Producto).filter(
        models.Producto.id == movimiento.producto_id).first()
    
    if producto:
        producto.cantidad += movimiento.cantidad
        producto.ultimo_movimiento = fecha_actual
    
    db.commit()
    
    # Obtener el movimiento recién creado para devolverlo
    nuevo_movimiento = db.query(models.Movimiento).filter(
        models.Movimiento.fecha == fecha_actual.date(),
        models.Movimiento.hora == fecha_actual.time(),
        models.Movimiento.cantidad == movimiento.cantidad,
        models.Movimiento.tipo == "Entrada",
        models.Movimiento.producto_id == movimiento.producto_id
    ).first()
    
    return schemas.Movimiento(
        id=nuevo_movimiento.id,
        fecha=nuevo_movimiento.fecha,
        hora = nuevo_movimiento.hora,
        cantidad=nuevo_movimiento.cantidad,
        tipo=nuevo_movimiento.tipo,
        producto_id=nuevo_movimiento.producto_id
    )


@app.post("/movimientos/salida/", response_model=schemas.Movimiento)
def create_movimiento_salida(movimiento: schemas.MovimientoCreate, db: Session = Depends(get_db)):
    fecha_actual = datetime.now()
    db_movimiento = models.Movimiento(
        fecha=fecha_actual.date(),
        cantidad=movimiento.cantidad,
        hora=fecha_actual.time(),
        tipo="Salida",
        producto_id=movimiento.producto_id
    )
     
    db.add(db_movimiento)
    producto = db.query(models.Producto).filter(
        models.Producto.id == movimiento.producto_id).first()
    if producto:
        producto.cantidad -= movimiento.cantidad
        producto.ultimo_movimiento = fecha_actual
    db.commit()
    db.refresh(db_movimiento)
    return db_movimiento


@app.post("/movimientos/salida/sql/", response_model=schemas.Movimiento)
def create_movimiento_salida_sql(movimiento: schemas.MovimientoCreate, db: Session = Depends(get_db)):
    fecha_actual = datetime.now()
    sql = text("INSERT INTO movimientos (fecha, hora, cantidad, tipo, producto_id) VALUES (:fecha, :hora, :cantidad, :tipo, :producto_id)")
    db.execute(sql, {'fecha': fecha_actual.date().isoformat(), 'hora': fecha_actual.time().isoformat(),'cantidad': movimiento.cantidad, 'tipo': "Salida", 'producto_id': movimiento.producto_id})
    
    producto = db.query(models.Producto).filter(
        models.Producto.id == movimiento.producto_id).first()
    
    if producto:
        producto.cantidad -= movimiento.cantidad
        producto.ultimo_movimiento = fecha_actual
    
    db.commit()
    
    # Obtener el movimiento recién creado para devolverlo
    nuevo_movimiento = db.query(models.Movimiento).filter(
        models.Movimiento.fecha == fecha_actual.date(),
        models.Movimiento.hora == fecha_actual.time(),
        models.Movimiento.cantidad == movimiento.cantidad,
        models.Movimiento.tipo == "Salida",
        models.Movimiento.producto_id == movimiento.producto_id
    ).first()
    
    return schemas.Movimiento(
        id=nuevo_movimiento.id,
        fecha=nuevo_movimiento.fecha,
        hora=nuevo_movimiento.hora,
        cantidad=nuevo_movimiento.cantidad,
        tipo=nuevo_movimiento.tipo,
        producto_id=nuevo_movimiento.producto_id
    )


@app.get("/productos/{producto_id}", response_model=schemas.Producto)
def read_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(
        models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto not found")
    return producto


@app.get("/productos/{producto_id}/movimientos/")
def read_producto_movimientos(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(
        models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto not found")
    movimientos = db.query(models.Movimiento).filter(
        models.Movimiento.producto_id == producto_id).all()
    return {"producto": producto, "movimientos": movimientos}
