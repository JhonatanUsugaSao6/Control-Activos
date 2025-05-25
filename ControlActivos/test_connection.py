


# import pyodbc

# try:
#     # Conexión a la base de datos SQL Server
#     conn = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};'
#         'SERVER=192.168.90.64;'
#         'DATABASE=UNOEE;'
#         'UID=power-bi;'
#         'PWD=Z1x2c3v4*'
#     )
#     cursor = conn.cursor()

#     # Nombre de la tabla que quieres consultar
#     tabla = 't121_mc_items_extensiones'

#     # Consultar los campos (columnas) de la tabla
#     cursor.execute("""
#         SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
#         FROM INFORMATION_SCHEMA.COLUMNS
#         WHERE TABLE_NAME = ?
#     """, (tabla,))

#     columnas = cursor.fetchall()

#     print(f"📄 Campos de la tabla '{tabla}':")
#     for nombre, tipo, nullable in columnas:
#         nulo = "✔️" if nullable == "YES" else "❌"
#         print(f"- {nombre} ({tipo}, Nulo: {nulo})")

# except Exception as e:
#     print("❌ Error al conectar o ejecutar la consulta:\n", e)

# finally:
#     if 'conn' in locals():
#         conn.close()
#         print("\n🔌 Conexión cerrada correctamente.")




#--------------------------------------------------------------------------------------------------------



# import pyodbc
# import pandas as pd
# import webbrowser

# try:
#     # Conexión a SQL Server
#     conn = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};'
#         'SERVER=192.168.90.64;'
#         'DATABASE=UNOEE;'
#         'UID=power-bi;'
#         'PWD=Z1x2c3v4*'
#     )

#     # Tabla a consultar
#     tabla = 't350_co_docto_contable '
#     query = f"SELECT TOP 10 * FROM {tabla}"

#     # Leer los datos en un DataFrame de pandas
#     df = pd.read_sql(query, conn)

#     # Guardar como archivo HTML
#     archivo_html = "registros.html"
#     df.to_html(archivo_html, index=False)

#     # Abrir en el navegador
#     webbrowser.open(archivo_html)

# except Exception as e:
#     print("❌ Error:", e)

# finally:
#     if 'conn' in locals():
#         conn.close()
#         print("🔌 Conexión cerrada.")








#---------- BUSCAR LA TABLA POR EL CAMPO ------------------------------------------------------------------------

# import pyodbc
# import os

# def buscar_tabla_por_campo(cursor, nombre_campo):
#     try:
#         query_buscar = """
#         SELECT 
#             t.name AS tabla,
#             c.name AS campo
#         FROM 
#             sys.tables AS t
#         INNER JOIN 
#             sys.columns AS c ON t.object_id = c.object_id
#         WHERE 
#             c.name LIKE ?
#         """
#         cursor.execute(query_buscar, f'%{nombre_campo}%')
#         resultados = cursor.fetchall()

#         if resultados:
#             print(f"✅ Tablas que contienen el campo '{nombre_campo}':")
#             for tabla, campo in resultados:
#                 print(f"- {tabla} (campo: {campo})")
#         else:
#             print(f"⚠️ No se encontró ninguna tabla que tenga el campo '{nombre_campo}'.")
#     except Exception as e:
#         print(f"❌ Error al buscar la columna: {e}")

# try:
#     conn = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};'
#         'SERVER=192.168.90.64;'
#         'DATABASE=UNOEE;'
#         'UID=power-bi;'
#         'PWD=Z1x2c3v4*'
#     )

#     cursor = conn.cursor()

#     # 👉 Opciones
#     opcion = input("¿Qué deseas hacer? (1 = Buscar columna / 2 = Ejecutar consulta por consecutivo): ")

#     if opcion == '1':
#         nombre_campo = input("🔎 Ingresa el nombre del campo que quieres buscar: ")
#         buscar_tabla_por_campo(cursor, nombre_campo)

#     elif opcion == '2':
#         consecutivo = input("🔢 Ingresa el consecutivo que quieres buscar: ")

#         query = """
#         SELECT 
#             t470.f470_rowid_item_ext AS Consecutivo,
#             t470.f470_id_fecha AS Fecha,
#             t150.f150_descripcion AS Bodega,
#             v121.v121_referencia AS Referencia,
#             v121.v121_descripcion AS Descripcion,
#             t121.f121_id_ext1_detalle AS Extension,
#             t470.f470_cant_q AS Cantidad,
#             t470.f470_id_unidad_medida AS UnidadMedida,
#             t155.f155_descripcion AS Proveedor,
#             t350.f350_usuario_aprobacion AS CreadoPor
#         FROM t470_triangulo AS t470
#         LEFT JOIN t150_mc_bodegas AS t150 ON t470.f470_id_bodega = t150.f150_id_bodega
#         LEFT JOIN v121 ON t470.f470_id_referencia = v121.v121_id
#         LEFT JOIN t121_extensiones AS t121 ON t470.f470_id_extension = t121.f121_id
#         LEFT JOIN t155_proveedores AS t155 ON t470.f470_id_proveedor = t155.f155_id
#         LEFT JOIN t350_usuarios AS t350 ON t470.f470_usuario_aprobacion = t350.f350_id
#         WHERE t470.f470_rowid_item_ext = ?
#         """

#         cursor.execute(query, consecutivo)
#         rows = cursor.fetchall()

#         if rows:
#             print("✅ Resultado de la consulta:")
#             for row in rows:
#                 print(dict(zip([column[0] for column in cursor.description], row)))
#         else:
#             print("⚠️ No se encontraron resultados para ese consecutivo.")

#     else:
#         print("❗ Opción inválida.")

# except Exception as e:
#     print("❌ Error al ejecutar la consulta:")
#     print(e)

# finally:
#     if 'conn' in locals():
#         conn.close()
#         print("🔌 Conexión cerrada.")




#----------------------------------------------------------------------------------------------------------------




# import pyodbc
# import os

# try:
#     # Conexión a la base de datos
#     conn = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};'
#         'SERVER=192.168.90.64;'
#         'DATABASE=UNOEE;'
#         'UID=power-bi;'
#         'PWD=Z1x2c3v4*'
#     )

#     cursor = conn.cursor()

#     print("✅ Conexión establecida.\n")

#     # Mostrar campos de t470_cm_movto_invent
#     print("📋 Columnas de t470_cm_movto_invent:")
#     query1 = "SELECT TOP 1 * FROM t470_cm_movto_invent"
#     cursor.execute(query1)
#     columns1 = [column[0] for column in cursor.description]
#     for col in columns1:
#         print(f" - {col}")

#     print("\n" + "-"*50 + "\n")

#     # Mostrar campos de t350_co_docto_contable
#     print("📋 Columnas de t350_co_docto_contable:")
#     query2 = "SELECT TOP 1 * FROM t350_co_docto_contable"
#     cursor.execute(query2)
#     columns2 = [column[0] for column in cursor.description]
#     for col in columns2:
#         print(f" - {col}")

# except Exception as e:
#     print("❌ Error al ejecutar la consulta:")
#     print(e)

# finally:
#     if 'conn' in locals():
#         conn.close()
#         print("\n🔌 Conexión cerrada.")





# ---------------------- CARGA LA INFORMACIÓN DEL INNER --------------------------------------------

# import pyodbc

# try:
#     conn = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};'
#         'SERVER=192.168.90.64;'
#         'DATABASE=UNOEE;'
#         'UID=power-bi;'
#         'PWD=Z1x2c3v4*'
#     )
#     cursor = conn.cursor()
#     print("✅ Conexión establecida.\n")

#     consecutivo = input("🔎 Ingresa el consecutivo f350_consec_docto que quieres buscar: ")

#     # Consulta corregida
#     query = f"""
#     SELECT
#         inv.f470_rowid,
#         inv.f470_rowid_bodega,
#         inv.f470_cant_1,
#         inv.f470_precio_uni,
#         inv.f470_vlr_neto,
#         inv. f470_id_unidad_medida,
#         cont.f350_consec_docto,
#         cont.f350_fecha,
#         cont.f350_total_db,
#         cont.f350_total_cr,
#         cont.f350_usuario_aprobacion
#     FROM t470_cm_movto_invent AS inv
#     INNER JOIN t350_co_docto_contable AS cont
#         ON inv.f470_rowid_docto = cont.f350_rowid
#     WHERE cont.f350_consec_docto = ?
#     """

#     cursor.execute(query, (consecutivo,))
#     rows = cursor.fetchall()

#     if rows:
#         print("\n🔎 Resultados encontrados:\n")
#         for row in rows:
#             print(row)
#     else:
#         print("\n⚠️ No se encontraron resultados para ese consecutivo.")

# except Exception as e:
#     print("❌ Error al ejecutar la consulta:")
#     print(e)

# finally:
#     if 'conn' in locals():
#         conn.close()
#         print("\n🔌 Conexión cerrada.")
        
        
        
        

#-------------------- BUSCAR ITEM EN TABLA O CAMPO DE LA BASE DE DATOS ---------------------------------------------

# import pyodbc

# conn_str = (
#     'DRIVER={ODBC Driver 17 for SQL Server};'
#     'SERVER=192.168.90.64;'
#     'DATABASE=UNOEE;'
#     'UID=power-bi;'
#     'PWD=Z1x2c3v4*'
# )

# search_value = 'RMDI0006'

# try:
#     conn = pyodbc.connect(conn_str)
#     cursor = conn.cursor()
#     print("✅ Conexión establecida.\n")

#     cursor.execute("""
#         SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME
#         FROM INFORMATION_SCHEMA.COLUMNS
#         WHERE DATA_TYPE IN ('char', 'varchar', 'nchar', 'nvarchar')
#         -- Puedes limitar por esquema si sabes que todo está en 'dbo':
#         -- AND TABLE_SCHEMA = 'dbo'
#     """)
#     columns = cursor.fetchall()

#     total = len(columns)
#     print(f"🔍 Buscando el valor '{search_value}' en {total} columnas tipo texto...\n")

#     for i, (schema, table, column) in enumerate(columns, 1):
#         print(f"[{i}/{total}] Buscando en {schema}.{table}.{column}...", end=' ')
#         try:
#             query = f"""
#                 SET LOCK_TIMEOUT 500;
#                 SELECT TOP 1 [{column}]
#                 FROM [{schema}].[{table}]
#                 WHERE [{column}] = ?
#             """
#             cursor.execute(query, (search_value,))
#             result = cursor.fetchone()
#             if result:
#                 print(f"✅ ENCONTRADO en {schema}.{table}.{column}")
#             else:
#                 print("No.")
#         except Exception as e:
#             print(f"⚠️ Error: {e}")

# except Exception as e:
#     print("❌ Error de conexión o consulta:")
#     print(e)

# finally:
#     if 'conn' in locals():
#         conn.close()
#         print("\n🔌 Conexión cerrada.")




#------------------------   COMO SABER LA RELACIÓN DE LAS TABLAS   -------------------------------------------------

# import pyodbc

# def encontrar_relacion():
#     conn_str = (
#         'DRIVER={ODBC Driver 17 for SQL Server};'
#         'SERVER=192.168.90.64;'
#         'DATABASE=UNOEE;'
#         'UID=power-bi;'
#         'PWD=Z1x2c3v4*'
#     )

#     try:
#         conn = pyodbc.connect(conn_str)
#         cursor = conn.cursor()

#         # Obtener columnas de la tabla t470
#         cursor.execute("SELECT TOP 1 * FROM t470_cm_movto_invent")
#         columnas = [desc[0] for desc in cursor.description]
#         fila = cursor.fetchone()

#         print("Columnas disponibles en t470_cm_movto_invent:")
#         for i, col in enumerate(columnas):
#             print(f"{i+1}. {col} = {fila[i]}")

#         print("\nBuscando posibles relaciones con t155_mc_ubicacion_auxiliares...\n")

#         for col in columnas:
#             query = f"""
#                 SELECT COUNT(*) FROM t470_cm_movto_invent AS inv
#                 JOIN t155_mc_ubicacion_auxiliares AS t155
#                 ON inv.{col} = t155.f155_id
#             """
#             try:
#                 cursor.execute(query)
#                 count = cursor.fetchone()[0]
#                 if count > 0:
#                     print(f"✔ Posible relación encontrada: inv.{col} = t155.f155_rowid ({count} coincidencias)")
#             except Exception as e:
#                 print(f"✖ No se pudo probar con el campo '{col}': {e}")

#         cursor.close()
#         conn.close()

#     except Exception as e:
#         print("❌ Error general:", e)

# if __name__ == "__main__":
#     encontrar_relacion()
    
    
    
    

#---------------------  MOSTRAR CAMPOS DE UN TABLA -------------------------------------------------------------

# import pyodbc

# # Conexión
# conn = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};'
#         'SERVER=192.168.90.64;'
#         'DATABASE=UNOEE;'
#         'UID=power-bi;'
#         'PWD=Z1x2c3v4*'
#     )
# cursor = conn.cursor()

# # Consulta columnas de la tabla t155_mc_ubicacion_auxiliares
# cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 't470_cm_movto_invent'")
# columns = cursor.fetchall()

# print("Columnas en t470_cm_movto_invent:")
# for col in columns:
#     print("-", col[0])

# cursor.close()
# conn.close()




#--------------------------------- DESCRIBIR TABLAS ------------------------------------------------------------

# import pyodbc

# def describir_tabla(nombre_tabla):
#     try:
#         conn = pyodbc.connect(
#         'DRIVER={ODBC Driver 17 for SQL Server};'
#         'SERVER=192.168.90.64;'
#         'DATABASE=UNOEE;'
#         'UID=power-bi;'
#         'PWD=Z1x2c3v4*'
#     )
#         cursor = conn.cursor()
#         cursor.execute(f"DESCRIBE {nombre_tabla}")
#         for fila in cursor.fetchall():
#             print(fila)
#     except Exception as e:
#         print("Error:", e)
#     finally:
#         cursor.close()
#         conn.close()






#------------------ CONSULTA DE KAREN CON LA TABLA V211 -----------------------------------

# import pyodbc

# conn = pyodbc.connect(
#     'DRIVER={ODBC Driver 17 for SQL Server};'
#     'SERVER=192.168.90.64;'
#     'DATABASE=UNOEE;'
#     'UID=power-bi;'
#     'PWD=Z1x2c3v4*'
# )

# # Límite de registros
# limite = 5

# cursor = conn.cursor()

# query = f"""
# SELECT TOP ({limite}) 
#     v121_descripcion, 
#     v121_id_item, 
#     v121_id_ext1_detalle, 
#     v121_rowid_item_ext, 
#     v121_referencia 
# FROM v121
# """

# cursor.execute(query)
# rows = cursor.fetchall()

# for row in rows:
#     print(row)

# cursor.close()
# conn.close()




#-------------- MIGRACIONES DE DJANGO EN SIESA -----------------------------------------------------------------


import pyodbc

# Conexión a SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=192.168.90.64;'
    'DATABASE=UNOEE;'
    'UID=power-bi;'
    'PWD=Z1x2c3v4*'
)

cursor = conn.cursor()

# Consulta para ver si existen tablas de Django
cursor.execute("""
SELECT name 
FROM sys.tables 
WHERE name LIKE 'django_%' OR name LIKE 'auth_%'
""")

tables = cursor.fetchall()

if tables:
    print("⚠ Se encontraron tablas de migraciones de Django en la base de datos SQL Server:")
    for table in tables:
        print("-", table[0])
else:
    print("✅ No se encontraron tablas de migraciones de Django. No se han ejecutado migraciones.")

conn.close()