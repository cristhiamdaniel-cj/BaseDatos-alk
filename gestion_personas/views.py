"""
Vistas para la gestión de contratistas y el dashboard.

Incluye:
- Funciones para renderizar formularios y páginas web.
- Operaciones CRUD para contratistas, integrando vistas y actualizaciones dinámicas.
- Consultas a la base de datos PostgreSQL.
- Indicadores visuales y consultas para el dashboard.
"""

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection, transaction
from django.views.decorators.csrf import csrf_exempt

# Usados para consultas avanzadas y manejo de datos
from sqlalchemy import create_engine
import pandas as pd


def listado_base(request):
    """
    Muestra la vista unificada con paginación de 50 registros por página.
    """
    with connection.cursor() as cursor:
        # Consulta SQL para obtener todos los registros de la vista_unificada ordenados por id_persona
        query = """
        SELECT *
        FROM vista_unificada
        ORDER BY id_persona ASC;
        """
        # Ejecutar la consulta en la base de datos
        cursor.execute(query)
        
        # Extraer los nombres de las columnas de la consulta
        columns = [col[0] for col in cursor.description]
        
        # Obtener todas las filas resultantes de la consulta
        rows = cursor.fetchall()

    # Configuración de paginación: dividir los resultados en bloques de 50 registros
    paginator = Paginator(rows, 50)  
    # Obtener el número de la página actual de los parámetros GET
    page = request.GET.get('page', 1)

    try:
        # Obtener los registros correspondientes a la página actual
        rows_paginated = paginator.page(page)
    except PageNotAnInteger:
        # Si la página no es un entero, mostrar la primera página
        rows_paginated = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página disponible
        rows_paginated = paginator.page(paginator.num_pages)

    # Renderizar la plantilla HTML con los datos
    return render(request, 'listado_base.html', {
        'columns': columns,          # Nombres de las columnas para generar encabezados dinámicos
        'rows': rows_paginated,      # Registros paginados
        'paginator': paginator,      # Objeto paginador para mostrar controles de navegación
    })


def lista_tablas(request):
    """
    Muestra una lista de tablas disponibles en el sistema.
    """
    # Definición de las tablas disponibles en el sistema
    tablas = [
        'areas',
        'caracteristicas_personales',
        'contratos',
        'familiar_social',
        'formacion_academica',
        'gestion_personas_persona',
        'hijos_familia',
        'identificacion',
        'lactancia_maternidad',
        'nota',
        'nota_persona',
        'pension_retiro',
        'personas',
        'proceso_contractual',
        'proceso_personas',
        'roles',
        'salud_pensiones',
        'subgrupos',
        'supervisores',
    ]

    # Renderizar la plantilla HTML con la lista de tablas
    # Pasar las tablas como contexto a la plantilla
    return render(request, 'lista_tablas.html', {
        'tablas': tablas  # Contexto: Lista de tablas para ser mostradas en la plantilla
    })


def campos_tabla(request, tabla):
    """
    Muestra los nombres y tipos de datos de las columnas de una tabla específica.

    Args:
        request (HttpRequest): La solicitud HTTP.
        tabla (str): El nombre de la tabla a consultar.

    Returns:
        HttpResponse: Renderiza una plantilla HTML con los nombres y tipos de columnas.
        JsonResponse: Devuelve un error en formato JSON si ocurre alguna excepción.
    """
    try:
        # Validación básica del nombre de la tabla para evitar inyecciones SQL
        if not tabla.isidentifier():
            return JsonResponse({'error': 'El nombre de la tabla es inválido.'}, status=400)

        # Consulta a la base de datos para obtener las columnas y sus tipos de datos
        with connection.cursor() as cursor:
            query = """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s;
            """
            cursor.execute(query, [tabla])  # Usamos parámetros para evitar inyecciones SQL
            columnas = cursor.fetchall()  # Devuelve una lista de tuplas (column_name, data_type)

        # Renderizamos la plantilla con el nombre de la tabla y sus columnas
        return render(request, 'campos_tabla.html', {
            'tabla': tabla,       # Nombre de la tabla
            'columnas': columnas  # Lista de columnas con su tipo de dato
        })

    except Exception as e:
        # Captura cualquier error y lo devuelve como respuesta JSON
        return JsonResponse({'error': f'Error al consultar las columnas de la tabla: {str(e)}'}, status=500)


def agregar_contratista(request):
    pass


def guardar_contratista(request):
    """
    Crea o actualiza un contratista en la base de datos.

    Este método maneja:
    - Actualizaciones de contratistas existentes mediante `id_persona`.
    - Creación de nuevos contratistas si `id_persona` no está presente.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    # Obtener los datos enviados en el formulario
    data = request.POST
    id_persona = data.get('id_persona')
    nombre = data.get('nombre')
    telefono = data.get('telefono')
    correo = data.get('correo')
    direccion = data.get('direccion')

    # Validar campos obligatorios
    if not all([nombre, telefono, correo]):
        return JsonResponse({'error': 'Faltan datos obligatorios (nombre, teléfono, correo).'}, status=400)

    try:
        # Usar una transacción atómica para garantizar la consistencia de los datos
        with transaction.atomic():
            with connection.cursor() as cursor:
                if id_persona:
                    # Actualizar un contratista existente
                    cursor.execute("""
                        UPDATE personas
                        SET primer_nombre = %s, telefono = %s, correo = %s, direccion = %s
                        WHERE id_persona = %s;
                    """, [nombre, telefono, correo, direccion, id_persona])
                else:
                    # Crear un nuevo contratista
                    cursor.execute("""
                        INSERT INTO personas (primer_nombre, telefono, correo, direccion)
                        VALUES (%s, %s, %s, %s) RETURNING id_persona;
                    """, [nombre, telefono, correo, direccion])
                    id_persona = cursor.fetchone()[0]

        # Respuesta exitosa con el ID del contratista creado o actualizado
        return JsonResponse({'success': True, 'id_persona': id_persona}, status=200)

    except Exception as e:
        # Manejo de errores con respuesta clara al cliente
        return JsonResponse({'error': f'Ocurrió un error al guardar los datos: {str(e)}'}, status=500)


@csrf_exempt
def obtener_subgrupos_roles(request):
    """
    Devuelve subgrupos o roles según el área o subgrupo seleccionados.

    Parámetros de la solicitud:
        - id_area: ID del área para obtener subgrupos.
        - id_subgrupo: ID del subgrupo para obtener roles.

    Respuestas:
        - JsonResponse con los subgrupos o roles dependiendo del parámetro proporcionado.
        - JsonResponse con error si no se proporcionan parámetros válidos.
    """
    id_area = request.GET.get('id_area')  # Obtener el ID del área desde los parámetros de la solicitud
    id_subgrupo = request.GET.get('id_subgrupo')  # Obtener el ID del subgrupo desde los parámetros de la solicitud

    try:
        # Caso: Obtener subgrupos basados en el ID del área
        if id_area:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_subgrupo, nombre_subgrupo FROM subgrupos WHERE id_area = %s", [id_area])
                subgrupos = [{'id': row[0], 'nombre': row[1]} for row in cursor.fetchall()]
            return JsonResponse({'subgrupos': subgrupos}, status=200)

        # Caso: Obtener roles basados en el ID del subgrupo
        if id_subgrupo:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_rol, nombre_rol FROM roles WHERE id_subgrupo = %s", [id_subgrupo])
                roles = [{'id': row[0], 'nombre': row[1]} for row in cursor.fetchall()]
            return JsonResponse({'roles': roles}, status=200)

        # Si no se proporciona ni id_area ni id_subgrupo
        return JsonResponse({'error': 'Debe proporcionar un id_area o un id_subgrupo'}, status=400)

    except Exception as e:
        # Manejo de errores durante la ejecución
        return JsonResponse({'error': f'Error al procesar la solicitud: {str(e)}'}, status=500)


@csrf_exempt
def actualizar_contratista(request, id_persona):
    """
    Renderiza la vista para actualizar los datos de un contratista.

    Parámetros:
        - request: Objeto HttpRequest.
        - id_persona: ID del contratista a actualizar.

    Respuestas:
        - GET: Devuelve un formulario con los datos del contratista pre-cargados.
        - Error 404 si el contratista no existe.
        - Error 500 en caso de fallo en la consulta o procesamiento.
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        with connection.cursor() as cursor:
            # Obtener datos del contratista desde la vista_unificada
            cursor.execute("SELECT * FROM vista_unificada WHERE id_persona = %s;", [id_persona])
            resultado = cursor.fetchone()

            if not resultado:
                return JsonResponse({'error': 'El contratista no existe'}, status=404)

            columnas = [col[0] for col in cursor.description]
            contratista = dict(zip(columnas, resultado))

            # Obtener áreas
            cursor.execute("SELECT id_area, nombre_area FROM areas;")
            areas = [{'id_area': row[0], 'nombre_area': row[1]} for row in cursor.fetchall()]

            # Obtener subgrupos relacionados con el área del contratista
            cursor.execute("SELECT id_subgrupo, nombre_subgrupo FROM subgrupos WHERE id_area = %s;", [contratista.get('id_area')])
            subgrupos = [{'id_subgrupo': row[0], 'nombre_subgrupo': row[1]} for row in cursor.fetchall()]

            # Obtener roles relacionados con el subgrupo del contratista
            cursor.execute("SELECT id_rol, nombre_rol FROM roles WHERE id_subgrupo = %s;", [contratista.get('id_subgrupo')])
            roles = [{'id_rol': row[0], 'nombre_rol': row[1]} for row in cursor.fetchall()]

        # Renderizar la plantilla con los datos necesarios
        return render(request, 'actualizar_contratista.html', {
            'contratista': contratista,
            'areas': areas,
            'subgrupos': subgrupos,
            'roles': roles,
        })

    except Exception as e:
        # Manejo de errores
        return JsonResponse({'error': f'Error al procesar la solicitud: {str(e)}'}, status=500)
    

@csrf_exempt
def eliminar_contratista(request, id_persona):
    """
    Elimina un contratista con base en su ID.

    Parámetros:
        - request: Objeto HttpRequest.
        - id_persona: ID del contratista a eliminar.

    Respuestas:
        - JSON con un mensaje de éxito si la operación es exitosa.
        - JSON con un mensaje de error y código 404 si el contratista no existe.
        - JSON con un mensaje de error y código 500 en caso de error del servidor.
    """
    try:
        with connection.cursor() as cursor:
            # Verificar si el contratista existe
            cursor.execute("""
                SELECT primer_nombre, segundo_nombre, apellido_paterno, apellido_materno
                FROM personas WHERE id_persona = %s;
            """, [id_persona])
            contratista = cursor.fetchone()

            if not contratista:
                # Contratista no encontrado
                return JsonResponse({'error': 'El contratista no existe'}, status=404)

            # Eliminar el contratista de la base de datos
            cursor.execute("DELETE FROM personas WHERE id_persona = %s;", [id_persona])

            # Formatear el nombre completo del contratista eliminado
            nombre_completo = " ".join(filter(None, contratista))
            return JsonResponse({
                'success': True,
                'message': f'El contratista {nombre_completo} ha sido eliminado correctamente.'
            })

    except Exception as e:
        # Manejo de errores en caso de excepciones durante la eliminación
        return JsonResponse({'error': f'Error al eliminar: {str(e)}'}, status=500)


def dashboard_view(request):
    """
    Genera la vista del dashboard con datos y visualizaciones clave.

    Incluye:
    - Indicadores generales sobre contratistas.
    - Histograma de días transcurridos desde la fecha de solicitud.
    - Lista de personas con más de 10 días desde la solicitud.
    - Métricas de completitud de datos.

    Respuestas:
        - Renderiza la plantilla 'dashboard.html' con los datos generados.
        - En caso de error, muestra un mensaje apropiado.
    """
    # Configuración de la base de datos
    DATABASE_URL = "postgresql://postgres:daniel@localhost/gestion_contratistas"
    engine = create_engine(DATABASE_URL)

    try:
        # --- 1. Consultar Indicadores SIPSE ---
        query_sipse = """
        SELECT 
            p.id_persona, 
            pc.numero_sipse
        FROM personas p
        LEFT JOIN proceso_personas pp ON p.id_persona = pp.id_persona
        LEFT JOIN proceso_contractual pc ON pp.id_proceso = pc.id_proceso;
        """
        df_sipse = pd.read_sql_query(query_sipse, con=engine)

        # Calcular métricas generales
        total_personas = df_sipse['id_persona'].nunique()
        personas_con_sipse = df_sipse['numero_sipse'].notnull().sum()
        personas_sin_sipse = total_personas - personas_con_sipse
        porcentaje_con_sipse = (personas_con_sipse / total_personas * 100) if total_personas > 0 else 0

        # --- 2. Generar Histograma de Días Transcurridos ---
        query_histograma = """
        SELECT 
            DATE_PART('day', age(CURRENT_DATE, pc.fecha_de_solicitud)) AS dias_transcurridos, 
            COUNT(*) AS cantidad_procesos
        FROM proceso_contractual pc
        WHERE pc.fecha_de_solicitud IS NOT NULL
        GROUP BY DATE_PART('day', age(CURRENT_DATE, pc.fecha_de_solicitud))
        ORDER BY dias_transcurridos;
        """
        df_histograma = pd.read_sql_query(query_histograma, con=engine)
        dias_transcurridos = {
            'x': df_histograma['dias_transcurridos'].tolist(),
            'y': df_histograma['cantidad_procesos'].tolist(),
        }

        # --- 3. Personas con más de 10 días desde la solicitud ---
        query_personas_mas_dias = """
        SELECT 
            p.id_persona,
            CONCAT(p.primer_nombre, ' ', COALESCE(p.segundo_nombre, ''), ' ', p.apellido_paterno, ' ', p.apellido_materno) AS nombre_completo,
            pc.numero_sipse,
            pc.fecha_de_solicitud,
            DATE_PART('day', age(CURRENT_DATE, pc.fecha_de_solicitud)) AS dias_transcurridos
        FROM personas p
        JOIN proceso_personas pp ON p.id_persona = pp.id_persona
        JOIN proceso_contractual pc ON pp.id_proceso = pc.id_proceso
        WHERE 
            pc.fecha_de_solicitud IS NOT NULL AND
            DATE_PART('day', age(CURRENT_DATE, pc.fecha_de_solicitud)) > 10
        ORDER BY dias_transcurridos DESC;
        """
        df_personas_mas_dias = pd.read_sql_query(query_personas_mas_dias, con=engine)
        personas_mas_dias = df_personas_mas_dias.to_dict(orient='records')

        # --- 4. Métricas de Completitud ---
        query_completitud = "SELECT * FROM vista_unificada;"
        df_completitud = pd.read_sql_query(query_completitud, con=engine)
        completitud = [
            {
                'column_name': column,
                'total_registros': len(df_completitud),
                'total_nulos': df_completitud[column].isnull().sum(),
                'porcentaje_completitud': round((1 - df_completitud[column].isnull().sum() / len(df_completitud)) * 100, 2),
            }
            for column in df_completitud.columns
        ]

        # --- 5. Preparar datos para la plantilla ---
        data = {
            'labels': ['Con SIPSE', 'Sin SIPSE'],
            'values': [int(personas_con_sipse), int(personas_sin_sipse)],
            'porcentaje_con_sipse': porcentaje_con_sipse,
            'total_personas': total_personas,
            'personas_con_sipse': personas_con_sipse,
            'personas_sin_sipse': personas_sin_sipse,
        }

        # Renderizar la plantilla con los datos
        return render(request, 'dashboard.html', {
            'data': data,
            'dias_transcurridos': dias_transcurridos,
            'personas_mas_dias': personas_mas_dias,
            'completitud': completitud
        })

    except Exception as e:
        # Manejo de errores con un mensaje claro
        error_message = f"Error al conectarse a la base de datos o procesar los datos: {e}"
        return render(request, 'dashboard.html', {'error': error_message})
    

def consulta_listado_base(request):
    """
    Permite realizar consultas dinámicas a la base de datos y muestra el resultado.

    Soporta:
    - Consultas SELECT: Devuelve resultados en formato tabla.
    - Operaciones INSERT, UPDATE, DELETE: Devuelve el número de filas afectadas.
    - Manejo de errores en caso de sintaxis incorrecta o consultas no válidas.
    """
    # Inicializar variables de respuesta
    resultado = None
    error = None
    message = None

    if request.method == 'POST':
        # Obtener la consulta del cuerpo del formulario
        query = request.POST.get('query', '').strip()

        # Validar que la consulta no esté vacía
        if not query:
            error = 'La consulta no puede estar vacía.'
        else:
            try:
                # Ejecutar la consulta en la base de datos
                with connection.cursor() as cursor:
                    cursor.execute(query)

                    # Manejar consultas SELECT
                    if query.lower().startswith('select'):
                        columns = [col[0] for col in cursor.description]
                        rows = cursor.fetchall()
                        resultado = {
                            'columns': columns,
                            'rows': rows,
                        }
                    else:
                        # Manejar operaciones que modifican datos
                        message = f"{cursor.rowcount} fila(s) afectada(s)."

            except Exception as e:
                # Capturar y devolver errores en la ejecución de la consulta
                error = f"Error al ejecutar la consulta: {str(e)}"

    # Renderizar la plantilla con los datos resultantes
    return render(request, 'consulta_listado_base.html', {
        'resultado': resultado,  # Resultados de una consulta SELECT
        'error': error,          # Mensaje de error en caso de fallo
        'message': message,      # Mensaje para operaciones exitosas
    })
