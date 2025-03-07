from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Inventario
from app import db
inv_estado = Blueprint('inventarios_estado', __name__)

def obtener_inventarios_por_estado(estado):
    """
    Obtiene la lista de inventarios según su estado.
    """
    inventarios = Inventario.query.filter(Inventario.estado == estado).all()
    
    for inv in inventarios:
        db.session.refresh(inv)

    lista_inventarios = []
    for i in inventarios:
        inventario_dict = {
            "docnum": i.docnum, 
            "almacen": i.almacen, 
            "estado": i.estado, 
            "fechaInicio": i.fechaInicio.strftime("%d-%m-%Y") if i.fechaInicio else None,
            "basedatos": i.basedatos.name
        }
        # Solo agregar fechaFin si el estado no es "Abierto"
        if estado != "Abierto":
            inventario_dict["fechaFin"] = i.fechaFin.strftime("%d-%m-%Y") if i.fechaFin else None
        lista_inventarios.append(inventario_dict)
    
    return lista_inventarios

@inv_estado.route('/inventarios_abiertos')
@login_required
def inventarios_abiertos():
    """
    Muestra la lista de inventarios con estado 'Abierto'.
    """
    lista_inventarios = obtener_inventarios_por_estado('Abierto')
    return render_template('inventarios.html', inventarios=lista_inventarios, titulo="Inventarios Abiertos")

@inv_estado.route('/inventarios_cerrados')
@login_required
def inventarios_cerrados():
    """
    Muestra la lista de inventarios con estado 'Cerrado'.
    """
    db.session.expire_all()
    inventario = Inventario.query.filter_by(docnum=16).first()
    print(inventario.estado)  # Debería imprimir 'Cerrado'
    lista_inventarios = obtener_inventarios_por_estado('Cerrado')
    return render_template('inventarios.html', inventarios=lista_inventarios, titulo="Inventarios Cerrados")
