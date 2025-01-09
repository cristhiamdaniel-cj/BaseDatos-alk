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

    # Insertar cada fila del DataFrame en la tabla salud_pensiones
    for _, row in df.iterrows():
        # Verificar que los datos de EPS, fondo de pensiones y ARL no sean nulos
        if not pd.isna(row['eps']) and not pd.isna(row['fondo_pensiones']) and not pd.isna(row['arl']):
            query = """
            INSERT INTO salud_pensiones (id_persona, eps, fondo_pensiones, arl)
            SELECT id_persona, %s, %s, %s
            FROM personas
            WHERE telefono = %s
            ON CONFLICT DO NOTHING;
            """
            cursor.execute(query, (
                row['eps'],  # EPS
                row['fondo_pensiones'],  # Fondo de pensiones
                row['arl'],  # ARL
                row['telefono']  # Teléfono para cruzar datos
            ))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla salud_pensiones")

except Exception as e:
    print(f"Error al insertar datos: {e}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
