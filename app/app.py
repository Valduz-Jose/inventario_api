from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    cantidad = db.Column(db.Integer, default=0)
    ultimo_movimiento = db.Column(db.DateTime, default=datetime.utcnow)

class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=datetime.utcnow)
    hora = db.Column(db.Time, default=datetime.utcnow().time)
    cantidad = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    producto = db.relationship('Producto', backref=db.backref('movimientos', lazy=True))

db.create_all()

@app.route('/producto', methods=['POST'])
def agregar_producto():
    data = request.json
    producto = Producto(nombre=data['nombre'], cantidad=data.get('cantidad', 0))
    db.session.add(producto)
    db.session.commit()
    return jsonify({'message': 'Producto agregado', 'producto': {'id': producto.id, 'nombre': producto.nombre}})

@app.route('/movimiento/entrada', methods=['POST'])
def agregar_movimiento_entrada():
    data = request.json
    producto = Producto.query.get(data['producto_id'])
    if producto:
        movimiento = Movimiento(fecha=datetime.utcnow().date(), hora=datetime.utcnow().time(),
                                cantidad=data['cantidad'], tipo='entrada', producto_id=producto.id)
        producto.cantidad += data['cantidad']
        producto.ultimo_movimiento = datetime.utcnow()
        db.session.add(movimiento)
        db.session.commit()
        return jsonify({'message': 'Movimiento de entrada agregado', 'movimiento': {'id': movimiento.id}})
    return jsonify({'message': 'Producto no encontrado'}), 404

@app.route('/movimiento/salida', methods=['POST'])
def agregar_movimiento_salida():
    data = request.json
    producto = Producto.query.get(data['producto_id'])
    if producto and producto.cantidad >= data['cantidad']:
        movimiento = Movimiento(fecha=datetime.utcnow().date(), hora=datetime.utcnow().time(),
                                cantidad=data['cantidad'], tipo='salida', producto_id=producto.id)
        producto.cantidad -= data['cantidad']
        producto.ultimo_movimiento = datetime.utcnow()
        db.session.add(movimiento)
        db.session.commit()
        return jsonify({'message': 'Movimiento de salida agregado', 'movimiento': {'id': movimiento.id}})
    return jsonify({'message': 'Producto no encontrado o cantidad insuficiente'}), 400

@app.route('/producto/<int:producto_id>', methods=['GET'])
def consultar_producto(producto_id):
    producto = Producto.query.get(producto_id)
    if (producto):
        movimientos = Movimiento.query.filter_by(producto_id=producto_id).all()
        movimientos_list = [{'id': m.id, 'fecha': m.fecha, 'hora': m.hora, 'cantidad': m.cantidad, 'tipo': m.tipo} for m in movimientos]
        return jsonify({'producto': {'id': producto.id, 'nombre': producto.nombre, 'cantidad': producto.cantidad, 'ultimo_movimiento': producto.ultimo_movimiento}, 'movimientos': movimientos_list})
    return jsonify({'message': 'Producto no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/movimiento/entrada/sql', methods=['POST'])
def agregar_movimiento_entrada_sql():
    data = request.json
    producto = db.session.execute('SELECT * FROM producto WHERE id = :id', {'id': data['producto_id']}).fetchone()
    if producto:
        db.session.execute('INSERT INTO movimiento (fecha, hora, cantidad, tipo, producto_id) VALUES (:fecha, :hora, :cantidad, :tipo, :producto_id)',
                           {'fecha': datetime.utcnow().date(), 'hora': datetime.utcnow().time(), 'cantidad': data['cantidad'], 'tipo': 'entrada', 'producto_id': data['producto_id']})
        db.session.execute('UPDATE producto SET cantidad = cantidad + :cantidad, ultimo_movimiento = :ultimo_movimiento WHERE id = :id',
                           {'cantidad': data['cantidad'], 'ultimo_movimiento': datetime.utcnow(), 'id': data['producto_id']})
        db.session.commit()
        return jsonify({'message': 'Movimiento de entrada agregado'})
    return jsonify({'message': 'Producto no encontrado'}), 404

@app.route('/movimiento/salida/sql', methods=['POST'])
def agregar_movimiento_salida_sql():
    data = request.json
    producto = db.session.execute('SELECT * FROM producto WHERE id = :id', {'id': data['producto_id']}).fetchone()
    if producto and producto.cantidad >= data['cantidad']:
        db.session.execute('INSERT INTO movimiento (fecha, hora, cantidad, tipo, producto_id) VALUES (:fecha, :hora, :cantidad, :tipo, :producto_id)',
                           {'fecha': datetime.utcnow().date(), 'hora': datetime.utcnow().time(), 'cantidad': data['cantidad'], 'tipo': 'salida', 'producto_id': data['producto_id']})
        db.session.execute('UPDATE producto SET cantidad = cantidad - :cantidad, ultimo_movimiento = :ultimo_movimiento WHERE id = :id',
                           {'cantidad': data['cantidad'], 'ultimo_movimiento': datetime.utcnow(), 'id': data['producto_id']})
        db.session.commit()
        return jsonify({'message': 'Movimiento de salida agregado'})
    return jsonify({'message': 'Producto no encontrado o cantidad insuficiente'}), 400

