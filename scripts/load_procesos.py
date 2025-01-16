import pandas as pd
import psycopg2
from coneccion import DB_CONFIG

# Ruta al archivo Excel
EXCEL_FILE = '../data_form/tarea_base.xlsx'

# Valores predeterminados según el tipo
DEFAULT_VALUES = {
    "date": "1901-01-01",
    "int": 0,
    "float": 0.0,
    "str": "desconocido"
}

def preprocess_row(row):
    """Preprocesa una fila asignando valores predeterminados según el tipo de dato."""
    processed_row = {
        "id_persona": int(row.get("id_persona", DEFAULT_VALUES["int"])) if pd.notna(row.get("id_persona")) else DEFAULT_VALUES["int"],
        "numero_sipse": str(row.get("numero_sipse", DEFAULT_VALUES["str"])) if pd.notna(row.get("numero_sipse")) else DEFAULT_VALUES["str"],
        "fecha_de_solicitud": str(row.get("fecha_de_solicitud", DEFAULT_VALUES["date"])) if pd.notna(row.get("fecha_de_solicitud")) else DEFAULT_VALUES["date"],
        "numero_de_no_hay": str(row.get("numero_de_no_hay", DEFAULT_VALUES["str"])) if pd.notna(row.get("numero_de_no_hay")) else DEFAULT_VALUES["str"],
        "cdp": str(row.get("cdp", DEFAULT_VALUES["str"])) if pd.notna(row.get("cdp")) else DEFAULT_VALUES["str"],
        "crp": str(row.get("crp", DEFAULT_VALUES["str"])) if pd.notna(row.get("crp")) else DEFAULT_VALUES["str"],
        "fecha_de_vencimiento": str(row.get("fecha_de_vencimiento", DEFAULT_VALUES["date"])) if pd.notna(row.get("fecha_de_vencimiento")) else DEFAULT_VALUES["date"],
        "abogado_a_cargo": str(row.get("abogado_a_cargo", DEFAULT_VALUES["str"])) if pd.notna(row.get("abogado_a_cargo")) else DEFAULT_VALUES["str"],
        "riesgo": float(row.get("riesgo", DEFAULT_VALUES["float"])) if pd.notna(row.get("riesgo")) else DEFAULT_VALUES["float"],
    }
    return processed_row

def main():
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Conexión exitosa a la base de datos")

        # Leer el archivo Excel
        df = pd.read_excel(EXCEL_FILE)

        for _, row in df.iterrows():
            # Preprocesar la fila
            processed_row = preprocess_row(row)

            # Logs para depuración
            print("\n--- Procesando Fila ---")
            for key, value in processed_row.items():
                print(f"{key}: {value} (tipo: {type(value)})")

            # Verificar si el proceso contractual ya existe
            cursor.execute("SELECT id_proceso FROM proceso_contractual WHERE numero_sipse = %s", (processed_row["numero_sipse"],))
            proceso = cursor.fetchone()

            if proceso:
                # Actualizar proceso contractual si ya existe
                id_proceso = proceso[0]
                print(f"Actualizando proceso contractual existente: id_proceso = {id_proceso}")
                cursor.execute("""
                    UPDATE proceso_contractual
                    SET fecha_de_solicitud = %s,
                        numero_de_no_hay = %s,
                        cdp = %s,
                        crp = %s,
                        fecha_de_vencimiento = %s,
                        abogado_a_cargo = %s,
                        riesgo = %s
                    WHERE id_proceso = %s
                """, (
                    processed_row["fecha_de_solicitud"], processed_row["numero_de_no_hay"], 
                    processed_row["cdp"], processed_row["crp"], 
                    processed_row["fecha_de_vencimiento"], 
                    processed_row["abogado_a_cargo"], processed_row["riesgo"], id_proceso
                ))
            else:
                # Insertar nuevo proceso contractual si no existe
                print("Insertando nuevo proceso contractual.")
                cursor.execute("""
                    INSERT INTO proceso_contractual (numero_sipse, fecha_de_solicitud, numero_de_no_hay, cdp, crp, fecha_de_vencimiento, abogado_a_cargo, riesgo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_proceso
                """, (
                    processed_row["numero_sipse"], processed_row["fecha_de_solicitud"], 
                    processed_row["numero_de_no_hay"], processed_row["cdp"], 
                    processed_row["crp"], processed_row["fecha_de_vencimiento"], 
                    processed_row["abogado_a_cargo"], processed_row["riesgo"]
                ))
                id_proceso = cursor.fetchone()[0]

            # Verificar si la relación persona-proceso ya existe
            if processed_row["id_persona"] != DEFAULT_VALUES["int"]:
                cursor.execute("""
                    SELECT 1 FROM proceso_personas WHERE id_persona = %s AND id_proceso = %s
                """, (processed_row["id_persona"], id_proceso))
                if not cursor.fetchone():
                    # Insertar relación persona-proceso si no existe
                    print("Insertando relación persona-proceso.")
                    cursor.execute("""
                        INSERT INTO proceso_personas (id_persona, id_proceso)
                        VALUES (%s, %s)
                    """, (processed_row["id_persona"], id_proceso))

        # Confirmar los cambios
        conn.commit()
        print("Datos procesados exitosamente.")

    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        # Cerrar la conexión
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None:
            conn.close()
            print("Conexión cerrada.")

if __name__ == "__main__":
    main()
