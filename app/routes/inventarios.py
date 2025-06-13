from io import BytesIO
from flask import Blueprint, flash, jsonify, redirect, render_template, request, send_file, url_for
from flask_login import login_required
import pandas as pd
from sqlalchemy import func
from app.models import Inventario, InventarioDetalle
from app import db
from utils import servicelayer

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
    #db.session.expire_all()
    lista_inventarios = obtener_inventarios_por_estado('Cerrado')
    return render_template('inventarios.html', inventarios=lista_inventarios, titulo="Inventarios Cerrados")

@inv_estado.route('/exportar_excel/<int:docnum>/<string:estado>')
@login_required
def exportar_excel(docnum, estado):
    try:
        # Depuración: Imprimir el docnum y el estado recibidos
        print(f"Exportando Excel para el inventario con docnum: {docnum}, estado: {estado}")

        # Obtener los detalles del inventario
        detalles = db.session.query(
            InventarioDetalle.itemcode,
            func.sum(InventarioDetalle.cantidad_contada).label('suma_cantidad'),
            func.sum(InventarioDetalle.diferencias).label('suma_diferencias')
        ).filter(InventarioDetalle.docnum == docnum) \
         .group_by(InventarioDetalle.itemcode) \
         .all()

        # Depuración: Imprimir los detalles obtenidos
        print(f"Detalles obtenidos para el inventario {docnum}: {detalles}")

        # Crear un DataFrame con los detalles
        data = {
            'Artículo': [detalle.itemcode for detalle in detalles],
            'Suma Cantidad': [detalle.suma_cantidad for detalle in detalles],
            'Diferencias': [detalle.suma_diferencias for detalle in detalles]
        }
        df = pd.DataFrame(data)

        # Depuración: Imprimir el DataFrame generado
        print(f"DataFrame generado:\n{df}")

        # Crear un archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Inventario')
        output.seek(0)  # Mover el cursor al inicio del archivo

        # Depuración: Confirmar que el archivo se generó correctamente
        print(f"Archivo Excel generado para el inventario {docnum}")

        # Enviar el archivo como respuesta
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'inventario_{docnum}.xlsx'
        )

    except Exception as e:
        # Depuración: Imprimir el error en la consola
        print(f"Error al exportar el inventario a Excel: {str(e)}")
        
        # Mostrar un mensaje de error al usuario
        flash(f"Error al exportar el inventario a Excel: {str(e)}", 'danger')
        
        # Redirigir a la página correcta según el estado
        if estado == 'Abierto':
            return redirect(url_for('inventarios_estado.inventarios_abiertos'))
        else:
            return redirect(url_for('inventarios_estado.inventarios_cerrados'))
        
@inv_estado.route('/crear_recuento_sap', methods=['POST'])
@login_required
def crear_recuento_sap_endpoint():
    try:
        data = request.get_json()
        docnum = data.get('docnum')

        if not docnum:
            return jsonify({'success': False, 'message': 'Falta el número de documento'}), 400

        # Llamar a la función del servicio
        resultado = servicelayer.crear_recuento_sap(docnum)

        if resultado['success']:
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500
