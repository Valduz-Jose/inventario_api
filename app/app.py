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
    ultimo_movimiento = db.Column(db.DateTime, default=datetime.now())

class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=datetime.now().date())
    hora = db.Column(db.Time, default=datetime.now().time())
    cantidad = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    producto = db.relationship('Producto', backref=db.backref('movimientos', lazy=True))

db.create_all()