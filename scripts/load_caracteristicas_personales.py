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

    # Insertar cada fila del DataFrame en la tabla caracteristicas_personales
    for _, row in df.iterrows():
        # Verificar que todos los campos necesarios no sean nulos
        if not pd.isna(row['rango_edad']) and not pd.isna(row['es_fumador']) and not pd.isna(row['consume_alcohol']) and not pd.isna(row['recibe_molestias_por_consumo']):
            query = """
            INSERT INTO caracteristicas_personales (id_persona, rango_edad, es_fumador, consume_alcohol, recibe_molestias_por_consumo)
            SELECT id_persona, %s, %s, %s, %s
            FROM personas
            WHERE telefono = %s
            ON CONFLICT DO NOTHING;
            """
            cursor.execute(query, (
                row['rango_edad'],  # Rango de edad
                row['es_fumador'],  # Es fumador
                row['consume_alcohol'],  # Consume alcohol
                row['recibe_molestias_por_consumo'],  # Recibe molestias por consumo
                row['telefono']  # Teléfono para cruzar datos
            ))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla caracteristicas_personales")

except Exception as e:
    print(f"Error al insertar datos: {e}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")

