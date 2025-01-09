import psycopg2
from coneccion import DB_CONFIG

# Estructura jerárquica de subgrupos y roles
subgrupos_roles = {
    "General": ["Asesor", "Secretario"],
    "Despacho Prensa": ["Jefe de prensa", "Publicista diseñador", "Realizador", "Community manager", "Periodista", "Apoyo a la gestión"],
    "Desarrollo Estratégico y Mejora": ["Auditor", "Promotor de la mejora", "Apoyo a la gestión"],
    "Jurídica": [
        "Abogado actuaciones administrativas",
        "Apoyo a la gestión",
        "Abogado mi casa me pertenece",
        "Abogado propiedad horizontal",
        "Abogado despachos comisorios",
        "Gran coordinador SEGURIDAD-AMBIENTE-RIESGOS-ESPACIO PÚBLICOS-HECHOS NOTORIOS",
        "Líder de equipo",
        "Profesional de calle",
        "Gestor de convivencia"
    ],
    "Relacionamiento Interinstitucional": ["Líder de equipo", "Profesional de apoyo", "Apoyo a la gestión"],
    "Comunicaciones": ["Jefe de prensa", "Publicista diseñador", "Realizador", "Community manager", "Periodista", "Apoyo a la gestión"],
    "Coordinación Administrativa y Financiera": ["Apoyo a la gestión", "Profesional de apoyo"],
    "PIGA": ["Referente PIGA", "Profesional PIGA"],
    "Servicios Generales y Funcionamiento": ["Toderos", "Conductor liviano", "Conductor pesado", "Conductor maquinaria"],
    "CDI y Atención al Usuario": ["Notificador motorizado", "Notificador en bicicleta", "Notificador a pie", "Radicador", "Coordinador"],
    "CPS y Planta": ["Líder", "Técnico SST", "Profesional de apoyo", "Apoyo a la gestión"],
    "TIC": ["Profesional", "Técnico", "Apoyo a la gestión"],
    "Gestión Documental": ["Técnico de archivo", "Bachiller", "Líder de proceso"],
    "Almacén": ["Profesional", "Técnico", "Apoyo a la gestión", "Logístico"],
    "Presupuesto": ["Profesional", "Apoyo a la gestión"],
    "Contabilidad": ["Profesional", "Apoyo a la gestión"],
    "Contratación": [
        "Abogado OPS",
        "Abogado licitaciones",
        "Apoyo a la gestión",
        "Profesional obligaciones por pagar",
        "Líder de sancionatorios",
        "Abogado sancionatorio"
    ],
    "Coordinación": ["Líder", "Formulador", "Apoyo a la supervisión"],
    "Subsidio Tipo C": ["Líder", "Profesional social", "Profesional de seguimiento", "Técnico SIRBE", "Apoyo a la gestión"],
    "Educación": ["Coordinador", "Formulador transversal", "Apoyo a la supervisión"],
    "Buen Trato": ["Coordinador", "Formulador transversal", "Apoyo a la supervisión"],
    "Salud": ["Coordinador", "Formulador transversal", "Apoyo a la supervisión"],
    "Cultura y Recreación": ["Profesor profesional", "Profesor técnico"],
    "Recreación y Deporte": ["Profesor profesional", "Profesor técnico"],
    "Reactivación Económica": ["Coordinador", "Formulador transversal", "Apoyo a la supervisión"],
    "Mujer": ["Coordinador", "Formulador transversal", "Apoyo a la supervisión"],
    "Ambiente": ["Coordinador", "Formulador transversal", "Apoyo a la supervisión"],
    "Paz, Memoria y Reconciliación": ["Coordinador", "Formulador transversal", "Apoyo a la supervisión"],
    "Seguridad": ["Coordinador", "Formulador transversal", "Apoyo a la supervisión"],
    "Infraestructura": ["Coordinador", "Formulador transversal", "Apoyo a la supervisión"],
    "Participación": ["Coordinador", "Formulador transversal", "Apoyo a la supervisión"],
    "Coordinación Policiva": ["Profesionales", "Apoyo a la gestión"],
    "Actuaciones Administrativas": ["Grupo de Jurídica"],
    "Hechos Notorios": ["Grupo de Jurídica (Calle, Espacio Público)"],
    "Cobro Persuasivo": ["Grupo de Jurídica", "Profesional cobro persuasivo"],
    "Calle": ["Gestor"],
    "Kennedy a la Medida": ["Líder", "Profesional", "Apoyo a la gestión"],
    "Demandas Mi Casa Me Pertenece": ["Abogados"],
    "Inspección": ["Abogado", "Ingeniero/Arquitecto", "Apoyo a la gestión"]
}

try:
    # Conectar a la base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Conexión exitosa a la base de datos")

    # Insertar roles para cada subgrupo
    for subgrupo, roles in subgrupos_roles.items():
        # Obtener el id_subgrupo de la tabla subgrupos
        cursor.execute("SELECT id_subgrupo FROM subgrupos WHERE nombre_subgrupo = %s;", (subgrupo,))
        subgrupo_id = cursor.fetchone()
        if not subgrupo_id:
            print(f"Subgrupo '{subgrupo}' no encontrado en la tabla subgrupos. Saltando...")
            continue
        subgrupo_id = subgrupo_id[0]

        # Insertar roles para este subgrupo
        for rol in roles:
            query = """
            INSERT INTO roles (id_subgrupo, nombre_rol)
            VALUES (%s, %s)
            ON CONFLICT (nombre_rol) DO NOTHING;
            """
            cursor.execute(query, (subgrupo_id, rol))

    # Confirmar los cambios en la base de datos
    conn.commit()
    print("Datos insertados exitosamente en la tabla roles")

except Exception as e:
    print(f"Error al insertar datos en la tabla roles: {e}")

finally:
    # Cerrar la conexión
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexión cerrada")
