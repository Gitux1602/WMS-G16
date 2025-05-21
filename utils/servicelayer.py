import requests
import json
from datetime import datetime
from app.models import Inventario, InventarioDetalle  

def conectar():
    url = "https://hanasrv:50000/b1s/v1/Login"
    
    payload = {
        "CompanyDB": "TIENDA",
        "Password": "fernando",
        "UserName": "manager"
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
    response.raise_for_status()
    api_response = response.json()
    sesion_id = api_response.get("SessionId")

    print(f"Conexión Exitosa {sesion_id}")
    return sesion_id

def crear_recuento_sap(docnum):
    """
    Crea un recuento en SAP basado en un inventario existente
    :param docnum: Número de documento del inventario
    :return: Diccionario con éxito/mensaje o error
    """
    try:
        # 1. Obtener datos del inventario desde la base de datos
        inventario = Inventario.query.get(docnum)
        if not inventario:
            return {'success': False, 'message': 'Inventario no encontrado'}
        
        if inventario.estado != 'Cerrado':
            return {'success': False, 'message': 'Solo se pueden crear recuentos de inventarios cerrados'}
        
        # 2. Obtener los detalles del inventario
        detalles = InventarioDetalle.query.filter_by(docnum=docnum).all()
        if not detalles:
            return {'success': False, 'message': 'No hay artículos en este inventario'}
        
        # 3. Preparar los datos para SAP
        inventory_lines = []
        for detalle in detalles:
            line = {
                "ItemCode": detalle.itemcode,
                "WarehouseCode": inventario.almacen,  # Siempre "T019"
                "Freeze": "tYES",
                "BinEntry": 9,  
                "CountedQuantity": detalle.cantidad_contada
            }
            inventory_lines.append(line)
        
        payload = {
            "BranchID": 11, 
            "InventoryCountingLines": inventory_lines,
            "Remarks": f"Conteo automático generado a partir del inventario {docnum}"
        }
        
        print("Datos a enviar a SAP:")
        print(json.dumps(payload, indent=4))
        
        # 4. Conectar a SAP y enviar el recuento
        session_id = conectar()
        url = "https://hanasrv:50000/b1s/v1/InventoryCountings"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": f"B1SESSION={session_id}"
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        response.raise_for_status()
        
        # 5. Procesar la respuesta
        sap_response = response.json()
        print("Respuesta de SAP:", sap_response)
        
        return {
            'success': True,
            'message': f"Recuento creado exitosamente en SAP (DocNum: {sap_response.get('DocNum')})",
            'docnum': sap_response.get('DocNum')
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error al conectar con SAP: {str(e)}"
        if hasattr(e, 'response') and e.response:
            try:
                error_detail = e.response.json()
                error_msg = f"{error_msg}. Detalles: {error_detail.get('error', {}).get('message', 'Sin detalles')}"
            except:
                error_msg = f"{error_msg}. Respuesta: {e.response.text}"
        return {'success': False, 'message': error_msg}
    
    except Exception as e:
        return {'success': False, 'message': f"Error inesperado: {str(e)}"}