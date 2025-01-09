import psycopg2
from coneccion import DB_CONFIG

# Estructura de datos de áreas y sus subgrupos
areas_subgrupos = {
    "Despacho": [
        "General",
        "Despacho Prensa",
        "Desarrollo Estratégico y Mejora",
        "Jurídica",
        "Relacionamiento Interinstitucional",
        "Comunicaciones"
    ],
    "Desarrollo Administrativo y Financiero": [
        "Coordinación Administrativa y Financiera",
        "PIGA",
        "Servicios Generales y Funcionamiento",
        "CDI y Atención al Usuario",
        "CPS y Planta",
        "TIC",
        "Gestión Documental",
        "Almacén",
        "Presupuesto",
        "Contabilidad",
        "Contratación"
    ],
    "Inversión Local": [
        "Coordinación",
        "Subsidio Tipo C",
        "Educación",
        "Buen Trato",
        "Salud",
        "Cultura y Recreación",
        "Recreación y Deporte",
        "Reactivación Económica",
        "Mujer",
        "Ambiente",
        "Paz, Memoria y Reconciliación",
        "Seguridad",
        "Infraestructura",
        "Participación"
    ],
    "Gestión Policiva y Jurídica": [
        "Coordinación Policiva",
        "Actuaciones Administrativas",
        "Hechos Notorios",
        "Cobro Persuasivo",
        "Calle",
        "Kennedy a la Medida",
        "Demandas Mi Casa Me Pertenece"
    ],
    "Inspecciones de Policía": [
        "Coordinación",
        "Inspección"
    ]
}

try:
    # Conectar a la base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Conexión exitosa a la base de datos")

    # Insertar subgrupos para cada área
    for area, subgrupos in areas_subgrupos.items():
        # Obtener el id_area de la tabla areas
        cursor.execute("SELECT id_area FROM areas WHERE nombre_area = %s;", (area,))
        area_id = cursor.fetchone()
        if not area_id:
            print(f"Área '{area}' no encontrada en la tabla areas. Saltando...")
            continue
        area_id = area_id[0]

        # Insertar subgrupos para esta área
        for subgrupo in subgrupos:
            query = """
            INSERT INTO subgrupos (id_area, nombre_subgrupo)
            VALUES (%s, %s)
            ON CONFLICT (nombre_subgrupo) DO NOTHING;
            """
            cursor.execute(query, (area_id, subgrupo))

    # Confirmar los cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla subgrupos")

except Exception as e:
    print(f"Error al insertar datos en la tabla subgrupos: {e}")

finally:
    # Cerrar la conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
