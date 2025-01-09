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

    # Insertar cada fila del DataFrame en la tabla pension_retiro
    for _, row in df.iterrows():
        # Verificar que los datos no sean nulos
        if not pd.isna(row['es_ultimo_anio_pension']) and not pd.isna(row['estimacion_pension']):
            query = """
            INSERT INTO pension_retiro (id_persona, es_ultimo_anio_pension, estimacion_pension)
            SELECT id_persona, %s, %s
            FROM personas
            WHERE telefono = %s
            ON CONFLICT DO NOTHING;
            """
            cursor.execute(query, (
                row['es_ultimo_anio_pension'],  # Último año de pensión
                row['estimacion_pension'],  # Estimación de pensión
                row['telefono']  # Teléfono para cruzar datos
            ))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla pension_retiro")

except Exception as e:
    print(f"Error al insertar datos: {e}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
