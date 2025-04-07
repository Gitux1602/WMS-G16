import pandas as pd
from app import create_app, db
from app.models import Articulo, Proveedor, CodigoBarras

app = create_app()
"""
#Crea articulos nuevos desde el excel llamado articulosnuevos y sus columnas son ItemCode, Description, FrgnName
with app.app_context():

    df = pd.read_excel('articulosnuevos.xlsx')


    print("Datos leídos del Excel:")
    print(df.head())

    
    for index, row in df.iterrows():
        nuevo_articulo = Articulo(
            itemcode=row['ItemCode'],
            descripcion=row['Description'],
            frngname=row['FrgnName']
        )
        db.session.add(nuevo_articulo)

    db.session.commit()
    print(f"\nSe han insertado {len(df)} artículos exitosamente.")
"""

with app.app_context():
    df = pd.read_excel('qrsnuevos.xlsx')
    
    for index, row in df.iterrows():
        articulo = Articulo.query.filter_by(itemcode=row['ItemCode']).first()
        proveedor = Proveedor.query.filter_by(proveedor_id=row['Supplier']).first()
        
        if not articulo or not proveedor:
            print(f"Fila {index}: Artículo/Proveedor no encontrado")
            continue
        
        qr = CodigoBarras.query.filter_by(codigo_barras=row['Qr']).first()
        if qr:
            continue
            
            
        db.session.add(
            CodigoBarras(
                codigo_barras=row['Qr'], 
                itemcode=articulo.itemcode,
                proveedor_id=proveedor.proveedor_id,
                pqt=row['Qty']
            )
        )
    
    db.session.commit()  
    print("Códigos de barras creados exitosamente.")

"""
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
"""