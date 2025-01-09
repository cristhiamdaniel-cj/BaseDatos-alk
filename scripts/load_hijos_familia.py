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

    # Insertar cada fila del DataFrame en la tabla hijos_familia
    for _, row in df.iterrows():
        # Verificar que los datos relevantes no sean nulos
        if not pd.isna(row['telefono']):
            query = """
            INSERT INTO hijos_familia (
                id_caracterizacion, numero_hijos, es_cabeza_familia, rango_edad_hijos, hijos_condicion_discapacidad, tipo_discapacidad
            )
            SELECT 
                cp.id_caracterizacion, 
                %s, %s, %s, %s, %s
            FROM caracteristicas_personales cp
            JOIN personas p ON p.id_persona = cp.id_persona
            WHERE p.telefono = %s
            ON CONFLICT DO NOTHING;
            """
            cursor.execute(query, (
                row.get('numero_hijos', None),  # Número de hijos
                row.get('es_cabeza_familia', None),  # Es cabeza de familia
                row.get('rango_edad_hijos', None),  # Rango de edad de los hijos
                row.get('hijos_condicion_discapacidad', None),  # Hijos con discapacidad
                row.get('tipo_discapacidad', None),  # Tipo de discapacidad
                row['telefono']  # Teléfono para cruzar datos
            ))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla hijos_familia")

except Exception as e:
    print(f"Error al insertar datos: {e}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
