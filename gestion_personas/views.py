from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse

# Vista para agregar un contratista
def agregar_contratista(request):
    with connection.cursor() as cursor:
        # Obtener áreas
        cursor.execute("SELECT id_area, nombre_area FROM areas;")
        areas = [{'id_area': row[0], 'nombre_area': row[1]} for row in cursor.fetchall()]

        # Obtener subgrupos
        cursor.execute("SELECT id_subgrupo, id_area, nombre_subgrupo FROM subgrupos;")
        subgrupos = [{'id_subgrupo': row[0], 'id_area': row[1], 'nombre_subgrupo': row[2]} for row in cursor.fetchall()]

        # Obtener roles
        cursor.execute("SELECT id_rol, id_subgrupo, nombre_rol FROM roles;")
        roles = [{'id_rol': row[0], 'id_subgrupo': row[1], 'nombre_rol': row[2]} for row in cursor.fetchall()]

    return render(request, 'agregar_contratista.html', {
        'areas': areas,
        'subgrupos': subgrupos,
        'roles': roles
    })



def eliminar_contratista(request):
    if request.method == 'POST':
        id_persona = request.POST.get('id_persona')
        if id_persona:
            with connection.cursor() as cursor:
                query = "DELETE FROM personas WHERE id_persona = %s;"
                cursor.execute(query, [id_persona])
            return JsonResponse({'success': True})
        return JsonResponse({'error': 'ID no proporcionado'}, status=400)
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)


# Función para devolver áreas, subgrupos, y roles (listas dependientes)
def obtener_subgrupos_roles(request):
    if request.method == 'GET':
        id_area = request.GET.get('id_area', None)
        id_subgrupo = request.GET.get('id_subgrupo', None)

        if id_area:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_subgrupo, nombre_subgrupo FROM subgrupos WHERE id_area = %s", [id_area])
                subgrupos = [{'id': row[0], 'nombre': row[1]} for row in cursor.fetchall()]
            return JsonResponse({'subgrupos': subgrupos})

        if id_subgrupo:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_rol, nombre_rol FROM roles WHERE id_subgrupo = %s", [id_subgrupo])
                roles = [{'id': row[0], 'nombre': row[1]} for row in cursor.fetchall()]
            return JsonResponse({'roles': roles})

    return JsonResponse({'error': 'Solicitud inválida'}, status=400)


# Función para crear o actualizar un registro
def guardar_contratista(request):
    if request.method == 'POST':
        data = request.POST
        id_persona = data.get('id_persona', None)  # Si es None, se creará un nuevo registro

        # Datos del formulario
        nombre = data.get('nombre')
        telefono = data.get('telefono')
        correo = data.get('correo')
        direccion = data.get('direccion')
        id_area = data.get('id_area')
        id_subgrupo = data.get('id_subgrupo')
        id_rol = data.get('id_rol')

        with connection.cursor() as cursor:
            if id_persona:
                # Actualizar
                query = """
                UPDATE personas
                SET primer_nombre = %s, telefono = %s, correo = %s, direccion = %s
                WHERE id_persona = %s;
                """
                cursor.execute(query, [nombre, telefono, correo, direccion, id_persona])
            else:
                # Crear
                query = """
                INSERT INTO personas (primer_nombre, telefono, correo, direccion)
                VALUES (%s, %s, %s, %s) RETURNING id_persona;
                """
                cursor.execute(query, [nombre, telefono, correo, direccion])
                id_persona = cursor.fetchone()[0]

            # Actualizar relación con área, subgrupo y rol
            cursor.execute("INSERT INTO roles (id_subgrupo, nombre_rol) VALUES (%s, %s) ON CONFLICT DO NOTHING;", [id_subgrupo, id_rol])

        return JsonResponse({'success': True, 'id_persona': id_persona})

    return JsonResponse({'error': 'Solicitud inválida'}, status=400)


# Vista para /listado_base
def listado_base(request):
    with connection.cursor() as cursor:
        query = """
        SELECT 
            p.id_persona, 
            p.primer_nombre, 
            p.segundo_nombre, 
            p.apellido_paterno, 
            p.apellido_materno, 
            p.genero, 
            p.telefono, 
            p.correo, 
            p.direccion, 
            i.numero_identificacion, 
            i.lugar_expedicion,
            fa.nivel_formacion,
            fa.area_formacion,
            cp.rango_edad,
            cp.es_fumador,
            cp.consume_alcohol,
            cp.recibe_molestias_por_consumo,
            fs.vivienda_propia,
            fs.personas_a_cargo,
            fs.relacion_parentesco,
            lm.estado_gestacion,
            lm.mes_gestacion,
            lm.fecha_parto,
            lm.fuente_lactante,
            hf.numero_hijos,
            hf.es_cabeza_familia,
            hf.rango_edad_hijos,
            hf.hijos_condicion_discapacidad,
            hf.tipo_discapacidad,
            sp.eps,
            sp.fondo_pensiones,
            sp.arl,
            pr.es_ultimo_anio_pension,
            pr.estimacion_pension,
            a.nombre_area AS area_nombre,
            s.nombre_subgrupo AS subgrupo_nombre,
            r.nombre_rol AS rol_nombre,
            sup.nombre_supervisor AS supervisor_nombre,
            c.estado_proceso,
            c.fecha_inicio_contrato,
            c.fecha_fin_contrato,
            c.numero_contrato,
            c.meses_antiguedad,
            c.honorarios_mes,
            c.objeto_contrato,
            c.numero_obligaciones
        FROM personas p
        LEFT JOIN identificacion i ON p.id_persona = i.id_persona
        LEFT JOIN formacion_academica fa ON p.id_persona = fa.id_persona
        LEFT JOIN caracteristicas_personales cp ON p.id_persona = cp.id_persona
        LEFT JOIN familiar_social fs ON cp.id_caracterizacion = fs.id_caracterizacion
        LEFT JOIN lactancia_maternidad lm ON cp.id_caracterizacion = lm.id_caracterizacion
        LEFT JOIN hijos_familia hf ON cp.id_caracterizacion = hf.id_caracterizacion
        LEFT JOIN salud_pensiones sp ON p.id_persona = sp.id_persona
        LEFT JOIN pension_retiro pr ON p.id_persona = pr.id_persona
        LEFT JOIN areas a ON a.id_area = p.id_persona -- Relación ejemplo, modificar según diseño
        LEFT JOIN subgrupos s ON s.id_area = a.id_area -- Relación ejemplo, modificar según diseño
        LEFT JOIN roles r ON r.id_subgrupo = s.id_subgrupo -- Relación ejemplo, modificar según diseño
        LEFT JOIN supervisores sup ON p.id_persona = sup.id_persona
        LEFT JOIN contratos c ON p.id_persona = c.id_persona
        ORDER BY p.id_persona DESC
        LIMIT 10;  -- Mostrar solo los últimos 10 registros
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    return render(request, 'listado_base.html', {'columns': columns, 'rows': rows})

# Vista para /tablas
def lista_tablas(request):
    tablas = [
        'personas', 
        'identificacion', 
        'formacion_academica', 
        'caracteristicas_personales', 
        'familiar_social', 
        'lactancia_maternidad', 
        'hijos_familia', 
        'salud_pensiones', 
        'pension_retiro',
        'areas', 
        'subgrupos', 
        'roles', 
        'supervisores', 
        'contratos'  # Incluimos la tabla contratos
    ]
    return render(request, 'lista_tablas.html', {'tablas': tablas})

# Vista para /tablas/<tabla>
def campos_tabla(request, tabla):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{tabla}';")
        columnas = cursor.fetchall()

    return render(request, 'campos_tabla.html', {'tabla': tabla, 'columnas': columnas})

# Vista para /listado_base/consulta
def consulta_listado_base(request):
    resultado = []
    error = None

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()

        if query:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    if query.lower().startswith('select'):
                        columns = [col[0] for col in cursor.description]
                        rows = cursor.fetchall()
                        resultado = {'columns': columns, 'rows': rows}
                    else:
                        resultado = f"Consulta ejecutada correctamente: {cursor.rowcount} filas afectadas."
            except Exception as e:
                error = str(e)
        else:
            error = "No se puede ejecutar una consulta vacía."

    return render(request, 'consulta_listado_base.html', {'resultado': resultado, 'error': error})

