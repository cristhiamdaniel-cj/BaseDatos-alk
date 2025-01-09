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

    # Insertar cada fila del DataFrame en la tabla formacion_academica
    for _, row in df.iterrows():
        # Verificar que los campos no sean nulos
        if not pd.isna(row['nivel_formacion']) and not pd.isna(row['area_formacion']):
            query = """
            INSERT INTO formacion_academica (id_persona, nivel_formacion, area_formacion)
            SELECT id_persona, %s, %s
            FROM personas
            WHERE telefono = %s
            ON CONFLICT DO NOTHING;
            """
            cursor.execute(query, (
                row['nivel_formacion'],  # nivel de formación
                row['area_formacion'],   # área de formación
                row['telefono']          # teléfono para cruzar datos
            ))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla formacion_academica")

except Exception as e:
    print(f"Error al insertar datos: {e}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")

