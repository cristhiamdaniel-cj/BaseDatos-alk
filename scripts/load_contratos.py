import pandas as pd
import psycopg2
from coneccion import DB_CONFIG

# Ruta al archivo CSV
CSV_FILE = '../data_form/formulario_filtered.csv'

def cast_to_date(value):
    """Convierte un valor a formato DATE o retorna None si es inválido."""
    try:
        return pd.to_datetime(value).date() if not pd.isna(value) else None
    except Exception:
        return None

try:
    # Conectar a la base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Conexión exitosa a la base de datos")
    
    # Leer el archivo CSV
    df = pd.read_csv(CSV_FILE)

    # Insertar cada fila del DataFrame en la tabla contratos
    for _, row in df.iterrows():
        # Verificar que los campos necesarios no sean nulos
        if not pd.isna(row['telefono']):
            query = """
            INSERT INTO contratos (
                id_persona,
                fecha_inicio,
                fecha_fin,
                numero_contrato,
                meses_antiguedad,
                honorarios_mes,
                objeto_contrato,
                numero_obligaciones
            )
            SELECT 
                p.id_persona, 
                %s, %s, %s, %s, %s, %s, %s
            FROM personas p
            WHERE p.telefono = %s
            ON CONFLICT DO NOTHING;
            """
            cursor.execute(query, (
                cast_to_date(row['fecha_inicio_contrato']),  # Fecha de inicio del contrato
                cast_to_date(row['fecha_fin_contrato']),  # Fecha de fin del contrato
                row['numero_contrato'],  # Número del contrato
                int(row['meses_antiguedad']) if not pd.isna(row['meses_antiguedad']) else None,  # Meses de antigüedad
                float(row['honorarios_mes']) if not pd.isna(row['honorarios_mes']) else None,  # Honorarios mensuales
                row['objeto_contrato'],  # Objeto del contrato
                int(row['numero_obligaciones']) if not pd.isna(row['numero_obligaciones']) else None,  # Número de obligaciones
                row['telefono']  # Teléfono para cruzar datos
            ))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla contratos")

except Exception as e:
    print(f"Error al insertar datos: {e}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
