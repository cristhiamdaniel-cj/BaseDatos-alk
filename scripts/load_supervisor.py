import pandas as pd
import psycopg2
from coneccion import DB_CONFIG

# Ruta al archivo CSV
CSV_FILE = '../data_form/formulario_filtered.csv'

try:
    # Conectar a la base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Conexión exitosa a la base de datos")
    
    # Leer el archivo CSV
    df = pd.read_csv(CSV_FILE)

    # Insertar cada fila del DataFrame en la tabla supervisores
    for _, row in df.iterrows():
        # Verificar que el supervisor tenga nombre y que podamos cruzar con el teléfono
        if not pd.isna(row['nombre_supervisor']) and not pd.isna(row['telefono']):
            query = """
            INSERT INTO supervisores (id_persona, nombre_supervisor)
            SELECT id_persona, %s
            FROM personas
            WHERE telefono = %s
            ON CONFLICT DO NOTHING;
            """
            cursor.execute(query, (
                row['nombre_supervisor'],  # Nombre del supervisor
                row['telefono']  # Teléfono para cruzar datos
            ))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla supervisores")

except Exception as e:
    print(f"Error al insertar datos: {e}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
