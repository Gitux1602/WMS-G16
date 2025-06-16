from decimal import Decimal
import requests
import json
from datetime import datetime
from app.models import Inventario, InventarioDetalle  
from utils.sap_conector import inventario_sap_subir_recuento

BASE_DATOS_MAP = {
    "DISTRIBUIDORA": {"db": "SBO_TIENDA", "branch_id": 11, "usa_bin": False},
    "FRONTERA": {"db": "SBO_TDAFRONTERA", "branch_id": 9, "usa_bin": True, "bin_entry": 1},
    "IDR": {"db": "IDR", "branch_id": 25, "usa_bin": False}
}

def conectar(basedatos):
    url = "https://hanasrv:50000/b1s/v1/Login"
    
    payload = {
        "CompanyDB": basedatos,
        "UserName": "manager",
        "Password": "fernando"
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
    response.raise_for_status()
    api_response = response.json()
    sesion_id = api_response.get("SessionId")

    print(f"Conexión Exitosa a {basedatos} - SessionId: {sesion_id}")
    return sesion_id

def crear_recuento_sap(docnum):
    try:
        inventario = Inventario.query.get(docnum)
        if not inventario:
            return {'success': False, 'message': 'Inventario no encontrado'}
        
        if inventario.estado != 'Cerrado':
            return {'success': False, 'message': 'Solo se pueden crear recuentos de inventarios cerrados'}

        detalles = InventarioDetalle.query.filter_by(docnum=docnum).all()
        if not detalles:
            return {'success': False, 'message': 'No hay artículos en este inventario'}

        nombre_empresa = inventario.basedatos.name.upper()
        config = BASE_DATOS_MAP.get(nombre_empresa)
        if not config:
            return {'success': False, 'message': f'No hay configuración para la empresa: {nombre_empresa}'}

        stock_sap = inventario_sap_subir_recuento(config["db"])  
        stock_dict = {
            row[0]: row[1]  # ItemCode: OnHand
            for row in stock_sap
        }

        print("\n" + "="*50)
        print("DETALLES DE STOCK Y DIFERENCIAS")
        print("="*50)
        print(f"{'ItemCode':<15} {'On Hand Actual':>15} {'Diferencia':>15} {'Nuevo Stock':>15}")
        print("-"*60)

        inventory_lines = []
        for detalle in detalles:
            item_code = detalle.itemcode
            diferencia = detalle.diferencias

            diferencia_decimal = Decimal(str(diferencia))
            on_hand_actual = stock_dict.get(item_code, Decimal('0')) 

            nuevo_stock = max(Decimal('0'), on_hand_actual + diferencia_decimal)

            # Imprimir los valores para cada artículo
            print(f"{item_code:<15} {float(on_hand_actual):>15.2f} {float(diferencia_decimal):>15.2f} {float(nuevo_stock):>15.2f}")

            line = {
                "ItemCode": item_code,
                "WarehouseCode": inventario.almacen,
                "Freeze": "tYES",
                "CountedQuantity": float(nuevo_stock)
            }

            if config.get("usa_bin"):
                line["BinEntry"] = config["bin_entry"]

            inventory_lines.append(line)

        print("="*60 + "\n")

        payload = {
            "BranchID": config["branch_id"],
            "InventoryCountingLines": inventory_lines,
            "Remarks": f"Conteo automático generado a partir del inventario {docnum}"
        }

        session_id = conectar(config["db"])
        url = "https://hanasrv:50000/b1s/v1/InventoryCountings"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Cookie": f"B1SESSION={session_id}"
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        response.raise_for_status()

        sap_response = response.json()
        #print("Respuesta de SAP:", sap_response)

        return {
            'success': True,
            'message': f"Recuento creado exitosamente en SAP (DocNum: {sap_response.get('DocumentNumber')})",
            'docnum': sap_response.get('DocNum')
        }

    except requests.exceptions.RequestException as e:
        error_msg = f"Error al conectar con SAP: {str(e)}"
        if hasattr(e, 'response') and e.response:
            try:
                error_detail = e.response.json()
                error_msg += f". Detalles: {error_detail.get('error', {}).get('message', 'Sin detalles')}"
            except:
                error_msg += f". Respuesta: {e.response.text}"
        return {'success': False, 'message': error_msg}

    except Exception as e:
        return {'success': False, 'message': f"Error inesperado: {str(e)}"}