from datetime import datetime
import math
from app import db
from app.models import Inventario, InventarioDetalle, Articulo, BaseDatosEnum, Ubicaciones, UBICACIONES_PREDEFINIDAS
from utils.sap_conector import bajar_inventario_desde_sap

def crear_conteo_inventario(basedatos):
    try:
        print(f"Base de datos recibida: {basedatos}")

        # Verificar que la base de datos sea válida
        if basedatos not in [bd.value for bd in BaseDatosEnum]:
            raise ValueError(f"Base de datos no válida: {basedatos}")

        # Obtener los datos de SAP
        resultados = bajar_inventario_desde_sap(basedatos)
        print(f"Resultados de SAP: {resultados}")

        if not resultados:
            raise ValueError("No se recibieron datos de SAP.")

        # Crear el documento de Inventario (cabecera)
        nuevo_inventario = Inventario(
            fechaInicio=datetime.utcnow(),
            almacen='T019',
            estado='Abierto',
            basedatos=BaseDatosEnum(basedatos) ) 
        db.session.add(nuevo_inventario)
        db.session.commit()
        print(f"Inventario creado con DocNum: {nuevo_inventario.docnum}")

        # Crear los detalles del Inventario
        for item in resultados:
            itemcode, onhand, whscode, itmsgrpnam = item

            # Convertir a float
            onhand = float(onhand)
            
            # Verificar si el artículo existe en la tabla Articulo
            articulo = Articulo.query.filter_by(itemcode=itemcode).first()
            if not articulo:
                print(f"Artículo {itemcode} no encontrado en la base de datos. Saltando...")
                continue

            # Crear el detalle del inventario
            nuevo_detalle = InventarioDetalle(
                docnum=nuevo_inventario.docnum,
                itemcode=itemcode,
                cantidad_almacen=onhand,
                cantidad_contada=0.0,
                diferencias=-onhand, 
                inventario=nuevo_inventario
            )
            db.session.add(nuevo_detalle)

        # Eliminar la inicialización automática de ubicaciones
        # nuevo_inventario.inicializar_ubicaciones()  # ¡Elimina esta línea!

        db.session.commit()
        print(f"Inventario {nuevo_inventario.docnum} guardado con éxito.")

        return nuevo_inventario

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        raise