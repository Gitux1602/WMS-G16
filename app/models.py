from enum import Enum
from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy import event
from datetime import date, datetime

# Función requerida por Flask-Login
@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    rol = db.Column(db.Integer, nullable=False, default=0)  # 0 = Usuario, 1 = Administrador

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Articulo(db.Model):
    itemcode = db.Column(db.String(50), primary_key=True)  
    descripcion = db.Column(db.String(255), nullable=False)
    frngname = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Articulo('{self.itemcode}', '{self.descripcion}', '{self.frngname}')"


class Proveedor(db.Model):
    proveedor_id = db.Column(db.String(50), primary_key=True)  
    nombre = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Proveedor('{self.proveedor_id}', '{self.nombre}', '{self.contacto}')"

class CodigoBarras(db.Model):
    codigo_barras = db.Column(db.String(100), primary_key=True)  #CatalagoIC del proveedor, para el PT019 CatalagoIC = ItemCode
    itemcode = db.Column(db.String(50), db.ForeignKey('articulo.itemcode'), nullable=False)  # Clave foránea a Artículos
    proveedor_id = db.Column(db.String(50), db.ForeignKey('proveedor.proveedor_id'), nullable=False)  # Clave foránea a Proveedores
    pqt = db.Column(db.Integer, nullable=False)  # Cantidad de piezas por paquete

    articulo = db.relationship('Articulo', backref=db.backref('codigos_barras', lazy=True))
    proveedor = db.relationship('Proveedor', backref=db.backref('codigos_barras', lazy=True))

    def __repr__(self):
        return f"CodigoBarras('{self.codigo_barras}', '{self.itemcode}', '{self.proveedor_id}', '{self.pqt}')"

class BaseDatosEnum(Enum):
    ACABADOS = "Acabados"
    IDR = "IDR"
    DISTRIBUIDORA = "Distribuidora"
    FRONTERA = "Frontera"


UBICACIONES_PREDEFINIDAS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", 
                            "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"]
class Inventario(db.Model):
    docnum = db.Column(db.Integer, primary_key=True)  
    fechaInicio = db.Column(db.Date, nullable=False, default=datetime.utcnow)  
    fechaFin = db.Column(db.Date, nullable=True)  
    almacen = db.Column(db.String(50), nullable=False, default='T019')
    estado = db.Column(db.String(20), nullable=False, default='Abierto') 
    comentarios = db.Column(db.String(100), nullable=True)  
    basedatos = db.Column(db.Enum(BaseDatosEnum), nullable=False)
    
    def __repr__(self):
        return f"Inventario('{self.docnum}', '{self.fechaInicio}', '{self.fechaFin}', '{self.almacen}', '{self.estado}')"

    def cerrar_documento(self):
        """
        Método para cerrar el documento y establecer la fechaFin.
        """
        if self.estado == 'Cerrado':
            raise ValueError("El documento ya está cerrado.")
    
        print(f"Cerrando documento {self.docnum}. FechaFin: {date.today()}") 
        self.fechaFin = date.today()  
        self.estado = 'Cerrado'  # Actualiza el estado
        print(f"Estado actualizado a 'Cerrado'. FechaFin: {self.fechaFin}")  
        db.session.commit()  # Guarda los cambios en la base de datos
        print("Cambios guardados en la base de datos.")  

#Prueba para ver como funcion event.listens_for
@event.listens_for(Inventario, 'before_insert')
@event.listens_for(Inventario, 'before_update')
def validate_comentarios_before_change(mapper, connection, target):
    if target.comentarios is not None and 'hola' in target.comentarios.lower():
        error_msg = f"Intento de guardar comentario no permitido en documento {target.docnum}: '{target.comentarios}'"
        print(f"ERROR VALIDACIÓN: {error_msg}")  # Esto se verá en la consola
        raise ValueError("El campo comentarios no puede contener la palabra 'hola'")
    
    # Mensaje de éxito (opcional)
    print(f"Comentarios validados correctamente para documento {target.docnum}")

class InventarioDetalle(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    docnum = db.Column(db.Integer, db.ForeignKey('inventario.docnum'), nullable=False)  
    itemcode = db.Column(db.String(50), db.ForeignKey('articulo.itemcode'), nullable=False)  
    cantidad_almacen = db.Column(db.Float, nullable=False)  
    cantidad_contada = db.Column(db.Float, nullable=False)  
    diferencias = db.Column(db.Float, nullable=False)  

    inventario = db.relationship('Inventario', backref=db.backref('detalles', lazy=True))
    articulo = db.relationship('Articulo', backref=db.backref('inventario_detalles', lazy=True))

    def __repr__(self):
        return f"InventarioDetalle('{self.id}', '{self.docnum}', '{self.itemcode}', '{self.cantidad_almacen}', '{self.cantidad_contada}', Diferencias: {self.diferencias})"


@event.listens_for(InventarioDetalle, 'before_insert')
@event.listens_for(InventarioDetalle, 'before_update')
def calcular_diferencias(mapper, connection, target):

    # Validar que cantidad_contada no sea nulo
    if target.cantidad_contada is None:
        raise ValueError("cantidad_contada no puede ser nulo.")
    
    # Validar que cantidad_contada no sea negativo
    if target.cantidad_contada < 0:
        raise ValueError("cantidad_contada no puede ser negativo.")
    
    # Si cantidad_almacen es nulo, asignar 0 
    if target.cantidad_almacen is None:
        target.cantidad_almacen = 0.0
    
    # Validar que cantidad_almacen no sea negativo
    if target.cantidad_almacen < 0:
        raise ValueError("cantidad_almacen no puede ser negativo.")
    
    # Calcular diferencias
    target.diferencias = target.cantidad_contada - target.cantidad_almacen

class Ubicaciones(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    docnum = db.Column(db.Integer, db.ForeignKey('inventario.docnum'), nullable=False)  
    itemcode = db.Column(db.String(50), db.ForeignKey('articulo.itemcode'), nullable=False)  
    ubicacion = db.Column(db.String(10), nullable=False)  # Ubicación (A, B, C, ..., T)
    cantidad_contada = db.Column(db.Float, nullable=False)  # Cantidad contada en esta ubicación

    inventario = db.relationship('Inventario', backref=db.backref('ubicaciones', lazy=True))
    articulo = db.relationship('Articulo', backref=db.backref('ubicaciones', lazy=True))
