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

    # Insertar cada fila del DataFrame en la tabla lactancia_maternidad
    for _, row in df.iterrows():
        # Verificar que los datos relevantes no sean nulos
        if not pd.isna(row['telefono']) and not pd.isna(row['estado_gestacion']):
            # Convertir fecha_parto a formato DATE, o manejar NaN
            fecha_parto = None
            if not pd.isna(row.get('fecha_parto', None)):
                try:
                    fecha_parto = pd.to_datetime(row['fecha_parto']).date()
                except Exception:
                    fecha_parto = None

            query = """
            INSERT INTO lactancia_maternidad (
                id_caracterizacion, estado_gestacion, mes_gestacion, fecha_parto, fuente_lactante
            )
            SELECT 
                cp.id_caracterizacion, 
                %s, %s, %s, %s
            FROM caracteristicas_personales cp
            JOIN personas p ON p.id_persona = cp.id_persona
            WHERE p.telefono = %s
            ON CONFLICT DO NOTHING;
            """
            cursor.execute(query, (
                row['estado_gestacion'],  # Estado de gestación
                row.get('mes_gestacion', None),  # Mes de gestación
                fecha_parto,  # Fecha de parto convertida
                row.get('fuente_lactante', None),  # Fuente lactante
                row['telefono']  # Teléfono para cruzar datos
            ))

    # Confirmar cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla lactancia_maternidad")

except Exception as e:
    print(f"Error al insertar datos: {e}")

finally:
    # Cerrar conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
