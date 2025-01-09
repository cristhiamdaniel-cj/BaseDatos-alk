import psycopg2
from coneccion import DB_CONFIG

# Lista de áreas a insertar
areas = [
    "Despacho",
    "Desarrollo Administrativo y Financiero",
    "Inversión Local",
    "Gestión Policiva y Jurídica",
    "Inspecciones de Policía"
]

try:
    # Conectar a la base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Conexión exitosa a la base de datos")

    # Insertar cada área en la tabla areas
    for area in areas:
        query = """
        INSERT INTO areas (nombre_area)
        VALUES (%s)
        ON CONFLICT (nombre_area) DO NOTHING;
        """
        cursor.execute(query, (area,))

    # Confirmar los cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla areas")

except Exception as e:
    print(f"Error al insertar datos en la tabla areas: {e}")

finally:
    # Cerrar la conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
