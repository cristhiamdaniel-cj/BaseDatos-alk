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

    # Insertar cada fila del DataFrame en la tabla personas
    for _, row in df.iterrows():
        query = """
        INSERT INTO personas (apellido_paterno, apellido_materno, primer_nombre, segundo_nombre, genero, telefono, correo, direccion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (correo) DO NOTHING;
        """
        cursor.execute(query, (
            row['apellido_paterno'], 
            row['apellido_materno'], 
            row['primer_nombre'], 
            row['segundo_nombre'],
            row['genero'], 
            row['telefono'], 
            row['correo'], 
            row['direccion']
        ))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente")

except Exception as e:
    print(f"Error al insertar datos: {e}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
