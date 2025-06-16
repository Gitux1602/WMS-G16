from hdbcli import dbapi
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

class Config:
    # Credenciales de SAP HANA
    SAP_HANA_HOST = os.getenv('SAP_HANA_HOST')
    SAP_HANA_PORT = int(os.getenv('SAP_HANA_PORT'))
    SAP_HANA_USER = os.getenv('SAP_HANA_USER')
    SAP_HANA_PASSWORD = os.getenv('SAP_HANA_PASSWORD')

    # Bases de datos
    BASES_DATOS = {
        "Distribuidora": "SBO_TIENDA",
        "Frontera": "SBO_TDAFRONTERA",
        "IDR": "IDR",
        "Acabados": "SBO_PINTADORA",
        "SBO_TIENDA": "SBO_TIENDA",
        "SBO_TDAFRONTERA": "SBO_TDAFRONTERA"        
    }

def conectar_a_sap(basedatos):
    try:
        schema = Config.BASES_DATOS.get(basedatos)
        if not schema:
            raise ValueError(f"Base de datos no válida: {basedatos}")

        conn = dbapi.connect(
            address=Config.SAP_HANA_HOST,
            port=Config.SAP_HANA_PORT,
            user=Config.SAP_HANA_USER,
            password=Config.SAP_HANA_PASSWORD
        )
        cursor = conn.cursor()
        return conn, cursor, schema
    except Exception as e:
        raise Exception(f"Error al conectar a SAP HANA: {e}")

def bajar_inventario_desde_sap(bd):
    try:

        conn, cursor, schema = conectar_a_sap(bd)

        query = f"""
        SELECT T0."ItemCode", T1."OnHand", T1."WhsCode", T2."ItmsGrpNam"
        FROM "{schema}".OITM T0
        INNER JOIN "{schema}".OITW T1 ON T0."ItemCode" = T1."ItemCode"
        INNER JOIN "{schema}".OITB T2 ON T0."ItmsGrpCod" = T2."ItmsGrpCod"
        WHERE T1."WhsCode" = 'T019'
        AND T2."ItmsGrpNam" IN ('ALUMINIO', 'EUROALUM', 'UNATRESOCTAVOS')
        """

        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close() 

        return resultados
    except Exception as e:
        raise Exception(f"Error al bajar el inventario desde SAP: {e}")
    
def inventario_sap_subir_recuento(basedatos):
    try:
        print(f"DEBUG - Valor de basedatos recibido: {basedatos}")
        conn, cursor, schema = conectar_a_sap(basedatos)

        query = f"""
        SELECT T0."ItemCode", T1."OnHand", T1."WhsCode", T2."ItmsGrpNam"
        FROM "{schema}".OITM T0
        INNER JOIN "{schema}".OITW T1 ON T0."ItemCode" = T1."ItemCode"
        INNER JOIN "{schema}".OITB T2 ON T0."ItmsGrpCod" = T2."ItmsGrpCod"
        WHERE T1."WhsCode" = 'T019'
        AND T2."ItmsGrpNam" IN ('ALUMINIO', 'EUROALUM', 'UNATRESOCTAVOS')
        """

        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        conn.close() 

        return resultados
    except Exception as e:
        raise Exception(f"Error al bajar el inventario desde SAP: {e}")
