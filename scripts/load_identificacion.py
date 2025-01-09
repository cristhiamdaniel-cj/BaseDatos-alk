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

    # Insertar cada fila del DataFrame en la tabla identificacion
    for _, row in df.iterrows():
        # Verificar que la identificación no sea nula
        if not pd.isna(row['identificacion']):
            query = """
            INSERT INTO identificacion (id_persona, numero_identificacion, lugar_expedicion)
            SELECT id_persona, %s, %s
            FROM personas
            WHERE telefono = %s
            ON CONFLICT (numero_identificacion) DO NOTHING;
            """
            cursor.execute(query, (
                row['identificacion'],  # número de identificación
                row['lugar_expedicion'],  # lugar de expedición
                row['telefono']  # teléfono para cruzar datos
            ))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla identificacion")

except Exception as e:
    print(f"Error al insertar datos: {e}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
