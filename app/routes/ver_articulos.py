from flask import render_template, Blueprint
from app import db
from app.models import Articulo

ver_articulos = Blueprint('ver_articulos', __name__)

@ver_articulos.route('/articulos', methods=['GET'])
def mostrar_articulos():
    # Obtener todos los artículos con sus códigos de barras relacionados
    articulos = Articulo.query.options(db.joinedload(Articulo.codigos_barras)).all()
    
    # Pasar los artículos a la plantilla
    return render_template('ver_articulos.html', articulos=articulos)