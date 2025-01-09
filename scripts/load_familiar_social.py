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

    # Insertar cada fila del DataFrame en la tabla familiar_social
    for _, row in df.iterrows():
        # Verificar que los datos relevantes no sean nulos
        if not pd.isna(row['telefono']) and not pd.isna(row['vivienda_propia']):
            query = """
            INSERT INTO familiar_social (id_caracterizacion, vivienda_propia, personas_a_cargo, relacion_parentesco)
            SELECT 
                cp.id_caracterizacion, 
                %s, %s, %s
            FROM caracteristicas_personales cp
            JOIN personas p ON p.id_persona = cp.id_persona
            WHERE p.telefono = %s
            ON CONFLICT DO NOTHING;
            """
            cursor.execute(query, (
                row['vivienda_propia'],  # Vivienda propia
                row.get('personas_a_cargo', None),  # Personas a cargo
                row.get('relacion_parentesco', None),  # Relación de parentesco
                row['telefono']  # Teléfono para cruzar datos
            ))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla familiar_social")

except Exception as e:
    print(f"Error al insertar datos: {e}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
