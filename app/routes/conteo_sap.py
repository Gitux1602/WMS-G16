from datetime import datetime
import os
import pandas as pd
from flask import Blueprint, jsonify, redirect, render_template, request, url_for, flash
from flask_login import login_required
from app.models import Articulo, BaseDatosEnum, CodigoBarras, Inventario, InventarioDetalle, Ubicaciones, UBICACIONES_PREDEFINIDAS
from services.inventario_services import crear_conteo_inventario
from app import db

inventario_bp = Blueprint('inventario', __name__)


@inventario_bp.route('/subir_excel', methods=['GET', 'POST'])
@login_required
def subir_excel():
    
    opciones_basedatos = [opcion.value for opcion in BaseDatosEnum]

    if request.method == 'POST':
        basedatos = request.form.get('basedatos')
        archivo_excel = request.files.get('archivo_excel')

        # Mensajes de depuración
        print("Archivo Excel recibido:", archivo_excel.filename)
        print("Base de datos seleccionada:", basedatos)

        # Validar que se haya seleccionado una base de datos y un archivo
        if not basedatos:
            flash('Debes seleccionar una base de datos', 'danger')
            return redirect(url_for('inventario.subir_excel'))

        if not archivo_excel or archivo_excel.filename == '':
            flash('Debes seleccionar un archivo Excel', 'danger')
            return redirect(url_for('inventario.subir_excel'))

        try:
            # Leer el archivo Excel
            df = pd.read_excel(archivo_excel, header=None)  # No tiene encabezados

            # Mensaje de depuración
            print("DataFrame leído:", df)

            # Validar el archivo
            if df.shape[1] != 2:
                flash('El archivo debe tener exactamente 2 columnas', 'danger')
                return redirect(url_for('inventario.subir_excel'))

            # Renombrar las columnas
            df.columns = ['articulo', 'piezas_almacen']

            # Crear un nuevo conteo de inventario
            print("Creando nuevo conteo de inventario...")
            nuevo_inventario = Inventario(
                fechaInicio=datetime.utcnow(),
                almacen='T019',  
                estado='Abierto', 
                basedatos=BaseDatosEnum(basedatos),  
            )
            db.session.add(nuevo_inventario)
            db.session.commit()
            print(f"Inventario creado con DocNum: {nuevo_inventario.docnum}")

            # Guardar los detalles del inventario
            for _, row in df.iterrows():
                itemcode = row['articulo']
                cantidad_almacen = float(row['piezas_almacen'])

                # Verificar si el artículo existe en la tabla Articulo
                articulo = Articulo.query.filter_by(itemcode=itemcode).first()
                if not articulo:
                    print(f"Artículo {itemcode} no encontrado en la base de datos. Saltando...")
                    continue

                # Crear el detalle del inventario
                nuevo_detalle = InventarioDetalle(
                    docnum=nuevo_inventario.docnum,
                    itemcode=itemcode,
                    cantidad_almacen=cantidad_almacen,
                    cantidad_contada=0.0, 
                    diferencias=-cantidad_almacen 
                )
                db.session.add(nuevo_detalle)

            db.session.commit()
            print(f"Inventario {nuevo_inventario.docnum} guardado con éxito.")

            # Redirigir a la página de mostrar_conteo_sap
            flash('Conteo creado exitosamente desde Excel', 'success')
            return redirect(url_for('inventario.mostrar_conteo_sap', docnum=nuevo_inventario.docnum))

        except Exception as e:
            db.session.rollback()
            print(f"Error al procesar el archivo Excel: {str(e)}")
            flash(f"Error al procesar el archivo Excel: {str(e)}", 'danger')
            return redirect(url_for('inventario.subir_excel'))

    return render_template('subir_excel.html', opciones_basedatos=opciones_basedatos)

#función para crear conteo de inventario mediante el service de HANA SQL
@inventario_bp.route('/crear_conteo', methods=['POST'])
@login_required
def crear_conteo():
    basedatos = request.form.get('basedatos')
    if not basedatos:
        flash('Debes seleccionar una base de datos', 'danger')
        return redirect(url_for('main.seleccionar_base_datos'))

    try:
        # Crear el conteo de inventario desde SAP
        nuevo_inventario = crear_conteo_inventario(basedatos)

        # Redirigir a la página de conteo_sap.html con el docnum del nuevo inventario
        return redirect(url_for('inventario.mostrar_conteo_sap', docnum=nuevo_inventario.docnum))
    except Exception as e:
        flash(f"Error al crear el conteo de inventario: {e}", 'danger')
        return redirect(url_for('main.seleccionar_base_datos'))


@inventario_bp.route('/conteo_sap/<int:docnum>')
@login_required
def mostrar_conteo_sap(docnum):
    """
    Muestra la página de conteo SAP para un documento de inventario específico.
    """
    #print("UBICACIONES_PREDEFINIDAS:", UBICACIONES_PREDEFINIDAS)  
    inventario = Inventario.query.get_or_404(docnum)
    detalles = InventarioDetalle.query.filter_by(docnum=docnum).all()
    
    # Calcular la sumatoria de cantidades contadas por artículo
    for detalle in detalles:
        # Sumar las cantidades contadas en todas las ubicaciones para este artículo
        sumatoria_cantidad = db.session.query(db.func.sum(Ubicaciones.cantidad_contada)) \
            .filter(Ubicaciones.docnum == docnum, Ubicaciones.itemcode == detalle.itemcode) \
            .scalar() or 0.0  # Si no hay registros, devuelve 0.0
        
        # Asignar la sumatoria al detalle
        detalle.sumatoria_cantidad = sumatoria_cantidad

        # Obtener las cantidades contadas por ubicación para cada detalle
        detalle.cantidades_por_ubicacion = {}
        for ubicacion in UBICACIONES_PREDEFINIDAS: 
            cantidad_ubicacion = db.session.query(db.func.sum(Ubicaciones.cantidad_contada)) \
                .filter(Ubicaciones.docnum == docnum, Ubicaciones.itemcode == detalle.itemcode, Ubicaciones.ubicacion == ubicacion) \
                .scalar() or 0.0
            detalle.cantidades_por_ubicacion[ubicacion] = cantidad_ubicacion
    
    return render_template('conteo_sap.html', inventario=inventario, detalles=detalles,UBICACIONES_PREDEFINIDAS=UBICACIONES_PREDEFINIDAS )

@inventario_bp.route('/actualizar_cantidad_contada/<int:detalle_id>', methods=['POST'])
@login_required
def actualizar_cantidad_contada(detalle_id):
    try:
        detalle = InventarioDetalle.query.get_or_404(detalle_id)
        data = request.get_json()
        cantidad_contada = float(data['cantidad_contada'])
        detalle.cantidad_contada = cantidad_contada  # Asigna la cantidad contada al detalle

        db.session.commit()

        return jsonify({'success': True, 'cantidad_contada': cantidad_contada})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@inventario_bp.route('/actualizar_cantidad_ubicacion/<int:detalle_id>', methods=['POST'])
@login_required
def actualizar_cantidad_ubicacion(detalle_id):
    """
    Actualiza la cantidad contada en una ubicación específica para un detalle de inventario.
    """
    try:
        detalle = InventarioDetalle.query.get_or_404(detalle_id)
        data = request.get_json()
        cantidad_contada = float(data['cantidad_contada'])
        ubicacion = data.get('ubicacion')

        # Busca si ya existe un registro en Ubicaciones para la combinación de docnum, itemcode y ubicacion
        ubicacion_obj = Ubicaciones.query.filter_by(
            docnum=detalle.docnum,
            itemcode=detalle.itemcode,
            ubicacion=ubicacion
        ).first()

        if not ubicacion_obj: #Si no existe o es none||vacio
            if cantidad_contada > 0: #y la cantidad contada es mayor que 0, crear un registro en Ubicaciones
                ubicacion_obj = Ubicaciones(
                    docnum=detalle.docnum,
                    itemcode=detalle.itemcode,
                    ubicacion=ubicacion,
                    cantidad_contada=cantidad_contada
                )
                db.session.add(ubicacion_obj)
            else:
                # Si la cantidad contada es 0, no crear un registro
                return jsonify({
                    'success': True,
                    'sumatoria_cantidad': 0.0,
                    'diferencias': -detalle.cantidad_almacen
                })
        else:
            # Si existe, actualizar la cantidad contada
            ubicacion_obj.cantidad_contada = cantidad_contada

        # Guardar los cambios en la base de datos
        db.session.commit()

        # Recalcular la sumatoria de cantidades contadas para este artículo
        sumatoria_cantidad = db.session.query(db.func.sum(Ubicaciones.cantidad_contada)) \
            .filter(Ubicaciones.docnum == detalle.docnum, Ubicaciones.itemcode == detalle.itemcode) \
            .scalar() or 0.0

        # Actualizar la cantidad contada en el detalle
        detalle.cantidad_contada = sumatoria_cantidad
        detalle.diferencias = sumatoria_cantidad - detalle.cantidad_almacen

        db.session.commit()

        return jsonify({
            'success': True,
            'sumatoria_cantidad': sumatoria_cantidad,
            'diferencias': detalle.diferencias
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inventario_bp.route('/obtener_cantidad_ubicacion/<int:detalle_id>', methods=['POST'])
@login_required
def obtener_cantidad_ubicacion(detalle_id):
    """
    Obtiene la cantidad contada en una ubicación específica para un detalle de inventario.
    """
    try:
        detalle = InventarioDetalle.query.get_or_404(detalle_id)
        data = request.get_json()
        ubicacion = data.get('ubicacion')

        # Buscar la ubicación en la base de datos
        ubicacion_obj = Ubicaciones.query.filter_by(
            docnum=detalle.docnum,
            itemcode=detalle.itemcode,
            ubicacion=ubicacion
        ).first()

        # Si no existe, devolver 0
        cantidad_contada = ubicacion_obj.cantidad_contada if ubicacion_obj else 0.0

        return jsonify({
            'success': True,
            'cantidad_contada': cantidad_contada
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
       
@inventario_bp.route('/cerrar_documento/<int:docnum>', methods=['POST'])
@login_required
def cerrar_documento(docnum):
    print(f"Recibido docnum: {docnum}")  
    inventario = Inventario.query.filter_by(docnum=docnum).first()
    if inventario:
        print(f"Documento encontrado: {inventario.docnum}")  
        try:
            inventario.cerrar_documento()  # Llama al método para cerrar el documento
            return jsonify({'success': True, 'message': 'Documento cerrado correctamente.'})
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400
    else:
        print("Documento no encontrado") 
        return jsonify({'success': False, 'message': 'Documento no encontrado.'}), 404
    
from flask import redirect, url_for

@inventario_bp.route('/actualizar_comentarios/<int:docnum>', methods=['POST'])
@login_required
def actualizar_comentarios(docnum):
    comentarios = request.form.get('comentarios')
    inventario = Inventario.query.filter_by(docnum=docnum).first()

    if inventario:
        try:
            inventario.comentarios = comentarios
            db.session.commit()
            flash("Comentarios actualizados correctamente.", "success")
        except Exception as e:
            flash("Error al guardar los comentarios.", "danger")
    else:
        flash("Documento no encontrado.", "warning")

    return redirect(url_for('inventario.mostrar_conteo_sap', docnum=docnum))


@inventario_bp.route('/procesar_codigo_qr', methods=['POST'])
@login_required
def procesar_codigo_qr():
    data = request.get_json()
    codigo_qr = data.get('codigo_qr')
    ubicacion = data.get('ubicacion')  # Ubicación seleccionada en el frontend

    #print(codigo_qr)
    
    if not codigo_qr or not ubicacion:
        return jsonify({"success": False, "message": "Código QR o ubicación no proporcionados"}), 400

    try:
        # Buscar el código de barras en la base de datos
        codigo_barras = CodigoBarras.query.filter_by(codigo_barras=codigo_qr).first()
        if not codigo_barras:
            return jsonify({"success": False, "message": "Código QR no encontrado"}), 404

        # Obtener el artículo y las piezas por paquete
        itemcode = codigo_barras.itemcode
        pqt = codigo_barras.pqt  # Piezas por paquete

        # Obtener el documento de inventario actual
        docnum = data.get('docnum') 
        inventario = Inventario.query.get_or_404(docnum)

        # Buscar el detalle del inventario para este artículo
        detalle = InventarioDetalle.query.filter_by(docnum=docnum, itemcode=itemcode).first()
        if not detalle:
            return jsonify({"success": False, "message": "Artículo no encontrado en el inventario"}), 404

        # Buscar o crear el registro en la tabla Ubicaciones
        ubicacion_obj = Ubicaciones.query.filter_by(
            docnum=docnum,
            itemcode=itemcode,
            ubicacion=ubicacion
        ).first()

        if not ubicacion_obj:
            ubicacion_obj = Ubicaciones(
                docnum=docnum,
                itemcode=itemcode,
                ubicacion=ubicacion,
                cantidad_contada=pqt  # Sumar las piezas por paquete
            )
            db.session.add(ubicacion_obj)
        else:
            ubicacion_obj.cantidad_contada += pqt  # Sumar las piezas por paquete

        # Guardar los cambios en la base de datos
        db.session.commit()

        # Recalcular la sumatoria de cantidades contadas para este artículo
        sumatoria_cantidad = db.session.query(db.func.sum(Ubicaciones.cantidad_contada)) \
            .filter(Ubicaciones.docnum == docnum, Ubicaciones.itemcode == itemcode) \
            .scalar() or 0.0

        # Obtener la cantidad contada en la ubicación seleccionada
        cantidad_ubicacion = ubicacion_obj.cantidad_contada

        # Actualizar la cantidad contada en el detalle
        detalle.cantidad_contada = sumatoria_cantidad
        detalle.diferencias = sumatoria_cantidad - detalle.cantidad_almacen

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Código QR procesado correctamente",
            "itemcode": itemcode,
            "descripcion": detalle.articulo.descripcion,  
            "sumatoria_cantidad": sumatoria_cantidad,
            "cantidad_ubicacion": cantidad_ubicacion,  
            "diferencias": detalle.diferencias
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error al procesar el código QR: {str(e)}"}), 500