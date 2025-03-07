from app import create_app, db
from app.models import Articulo, Proveedor,  CodigoBarras

app = create_app()
"""
with app.app_context():
    # Crear artículos de ejemplo
    articulos = [
        Articulo(itemcode="7518SA", descripcion="Perfil de aluminio Jamba", frngname="P0001"),
        Articulo(itemcode="7333SA", descripcion="Perfil de aluminio Mosquiter", frngname="P0001"),
    ]

    # Agregar artículos a la sesión
    for articulo in articulos:
        db.session.add(articulo)

    # Guardar los cambios en la base de datos
    db.session.commit()
    print("Datos iniciales de artículos cargados exitosamente.")

with app.app_context():
    proveedores = [
        Proveedor(proveedor_id="P0008", nombre="Extrusiones Metalicas")
    ]
    
    # Agregar los proveedores a la sesión
    db.session.add_all(proveedores)
    
    # Guardar cambios en la base de datos
    db.session.commit()
    
    print("Datos iniciales de proveedores cargados exitosamente.")

"""

with app.app_context():
    
    articulo = Articulo.query.filter_by(itemcode="7518SA").first()
    proveedor = Proveedor.query.filter_by(proveedor_id="P0008").first()

    if articulo and proveedor:
        codigos_barras = [
            CodigoBarras(
                codigo_barras="2", 
                itemcode=articulo.itemcode,
                proveedor_id=proveedor.proveedor_id,
                pqt=10 
            )
        ]

        
        db.session.add_all(codigos_barras)

        # Guardamos los cambios
        db.session.commit()
        print("Datos iniciales de códigos de barras cargados exitosamente.")
    else:
        print("No se encontraron los datos relacionados.")
