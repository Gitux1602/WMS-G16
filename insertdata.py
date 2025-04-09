#import pandas as pd
from app import create_app, db
from app.models import CodigoBarras, Proveedor, Articulo,  CodigoBarras, User

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
"""
#Crea QR's nuevos desde el excel llamado qrsnuevos y sus columnas son ItemCode, Supplier, Qr, Qty
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
"""
#Crea proveedores desde la lista proveedores
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
#Renombra el campo nombre de la tabla proveedor
with app.app_context():
    proveedor = Proveedor.query.get("P0008")
    
    if proveedor:
        proveedor.nombre = "EXTRUSIONES METALICAS"
        
        # Guardar cambios
        db.session.commit()
        print("Nombre del proveedor actualizado correctamente.")
    else:
        print("Proveedor no encontrado.")
"""
"""
#Elimina C.Barras
with app.app_context():
    codigo = CodigoBarras.query.get("120500006100563M0E")
    if codigo:
        db.session.delete(codigo)
        db.session.commit()
        print("Código de barras eliminado.")
    else:
        print("Código no encontrado.")
"""
"""
#Elimina Proveedor
with app.app_context():
    proveedor = Proveedor.query.get("P0002")
    
    if proveedor:
        db.session.delete(proveedor)
        
        db.session.commit()
        print("Proveedor eliminado correctamente.")
    else:
        print("Proveedor no encontrado.")
"""
#Asigna rol de administrador = (1) dado el User.query.get(id) de la tabla User
with app.app_context():
    usuarioadmin = User.query.get(2)

    if usuarioadmin:
        usuarioadmin.rol = 0
        
        # Guardar cambios
        db.session.commit()
        print("Rol de usuario actualizado correctamente a admin")
    else:
        print("Usuario no encontrado")