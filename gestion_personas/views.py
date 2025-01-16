"""
Vistas para la gestión de contratistas y dashboard en Django.

Este módulo incluye:
- Vistas para renderizar páginas HTML.
- Conexiones a la base de datos PostgreSQL usando SQLAlchemy y Django.
- Funciones para realizar operaciones CRUD y consultas dinámicas.
- Indicadores y visualizaciones para un dashboard interactivo.
"""

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.db import connection, transaction
from django.http import JsonResponse
from sqlalchemy import create_engine
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd

@csrf_exempt
def actualizar_contratista(request, id_persona):
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                # Obtener el contratista
                cursor.execute("SELECT * FROM vista_unificada WHERE id_persona = %s;", [id_persona])
                resultado = cursor.fetchone()
                columnas = [col[0] for col in cursor.description]

                if not resultado:
                    return JsonResponse({'error': 'El contratista no existe'}, status=404)

                contratista = dict(zip(columnas, resultado))

                # Obtener las áreas
                cursor.execute("SELECT id_area, nombre_area FROM areas;")
                areas = [{'id_area': row[0], 'nombre_area': row[1]} for row in cursor.fetchall()]

                # Obtener subgrupos
                cursor.execute("SELECT id_subgrupo, nombre_subgrupo FROM subgrupos WHERE id_area = %s;", [contratista['id_area']])
                subgrupos = [{'id_subgrupo': row[0], 'nombre_subgrupo': row[1]} for row in cursor.fetchall()]

                # Obtener roles
                cursor.execute("SELECT id_rol, nombre_rol FROM roles WHERE id_subgrupo = %s;", [contratista['id_subgrupo']])
                roles = [{'id_rol': row[0], 'nombre_rol': row[1]} for row in cursor.fetchall()]

            return render(request, 'actualizar_contratista.html', {
                'contratista': contratista,
                'areas': areas,
                'subgrupos': subgrupos,
                'roles': roles,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



def dashboard_view(request):
    # Configuración de la base de datos
    DATABASE_URL = "postgresql://postgres:daniel@localhost/gestion_contratistas"
    engine = create_engine(DATABASE_URL)

    try:
        # Consulta principal: Indicadores SIPSE
        query = """
        SELECT 
            p.id_persona, 
            pc.numero_sipse
        FROM personas p
        LEFT JOIN proceso_personas pp ON p.id_persona = pp.id_persona
        LEFT JOIN proceso_contractual pc ON pp.id_proceso = pc.id_proceso;
        """
        df = pd.read_sql_query(query, con=engine)

        # Indicadores generales
        total_personas = df['id_persona'].nunique()
        personas_con_sipse = df['numero_sipse'].notnull().sum()
        personas_sin_sipse = total_personas - personas_con_sipse
        porcentaje_con_sipse = (personas_con_sipse / total_personas) * 100 if total_personas > 0 else 0

        # Histograma de días transcurridos desde la fecha de solicitud
        dias_transcurridos_query = """
        SELECT 
            DATE_PART('day', age(CURRENT_DATE, pc.fecha_de_solicitud)) AS dias_transcurridos, 
            COUNT(*) AS cantidad_procesos
        FROM proceso_contractual pc
        WHERE pc.fecha_de_solicitud IS NOT NULL
        GROUP BY DATE_PART('day', age(CURRENT_DATE, pc.fecha_de_solicitud))
        ORDER BY dias_transcurridos;
        """
        dias_transcurridos_df = pd.read_sql_query(dias_transcurridos_query, con=engine)
        dias_transcurridos = {
            'x': dias_transcurridos_df['dias_transcurridos'].tolist(),
            'y': dias_transcurridos_df['cantidad_procesos'].tolist(),
        }

        # Consulta para personas con más de 10 días desde la fecha de solicitud
        personas_mas_dias_query = """
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
        personas_mas_dias_df = pd.read_sql_query(personas_mas_dias_query, con=engine)
        personas_mas_dias = personas_mas_dias_df.to_dict(orient='records')

        # Consulta de completitud de datos
        query = """
        SELECT * FROM vista_unificada;
        """
        df = pd.read_sql_query(query, con=engine)
        # Completitud de datos
        completitud = []
        for column in df.columns:
            total_registros = len(df)
            total_nulos = df[column].isnull().sum()
            porcentaje_completitud = round((1 - total_nulos / total_registros) * 100, 2)
            completitud.append({
                'column_name': column,
                'total_registros': total_registros,
                'total_nulos': total_nulos,
                'porcentaje_completitud': porcentaje_completitud
            })

        # Preparar datos para el template
        data = {
            'labels': ['Con SIPSE', 'Sin SIPSE'],
            'values': [int(personas_con_sipse), int(personas_sin_sipse)],
            'porcentaje_con_sipse': porcentaje_con_sipse,
            'total_personas': total_personas,
            'personas_con_sipse': personas_con_sipse,
            'personas_sin_sipse': personas_sin_sipse,
        }

        # Renderizar la página con los datos
        return render(request, 'dashboard.html', {
            'data': data,
            'dias_transcurridos': dias_transcurridos,
            'personas_mas_dias': personas_mas_dias,
            'completitud': completitud
        })

    except Exception as e:
        # Manejo de errores
        error_message = f"Error al conectarse a la base de datos o procesar los datos: {e}"
        return render(request, 'dashboard.html', {'error': error_message})

@csrf_exempt
def eliminar_contratista(request, id_persona):
    """
    Elimina un contratista con base en su ID.
    """
    if request.method == 'POST':  # Asegúrate de que sea una solicitud POST
        try:
            with connection.cursor() as cursor:
                # Verifica si existe el contratista
                cursor.execute("""
                    SELECT primer_nombre, segundo_nombre, apellido_paterno, apellido_materno 
                    FROM personas WHERE id_persona = %s;
                """, [id_persona])
                contratista = cursor.fetchone()

                if not contratista:
                    return JsonResponse({'error': 'El contratista no existe'}, status=404)

                # Eliminar el contratista
                cursor.execute("DELETE FROM personas WHERE id_persona = %s;", [id_persona])

                nombre_completo = " ".join(filter(None, contratista))
                return JsonResponse({
                    'success': True,
                    'message': f'El contratista {nombre_completo} ha sido eliminado correctamente.'
                })
        except Exception as e:
            return JsonResponse({'error': f'Error al eliminar: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Vista para agregar un contratista
def agregar_contratista(request):
    """
    Muestra las áreas, subgrupos y roles necesarios para agregar un contratista.
    """
    try:
        with connection.cursor() as cursor:
            query = """
            SELECT 
                a.id_area, a.nombre_area, 
                s.id_subgrupo, s.nombre_subgrupo, 
                r.id_rol, r.nombre_rol 
            FROM areas a
            LEFT JOIN subgrupos s ON s.id_area = a.id_area
            LEFT JOIN roles r ON r.id_subgrupo = s.id_subgrupo;
            """
            cursor.execute(query)
            data = cursor.fetchall()

        areas, subgrupos, roles = [], [], []
        for row in data:
            areas.append({'id_area': row[0], 'nombre_area': row[1]})
            subgrupos.append({'id_subgrupo': row[2], 'nombre_subgrupo': row[3]})
            roles.append({'id_rol': row[4], 'nombre_rol': row[5]})

        return render(request, 'agregar_contratista.html', {
            'areas': areas,
            'subgrupos': subgrupos,
            'roles': roles
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Función para devolver subgrupos y roles basados en un área o subgrupo
@csrf_exempt
def obtener_subgrupos_roles(request):
    """
    Devuelve subgrupos o roles según el área o subgrupo seleccionados.
    """
    id_area = request.GET.get('id_area')
    id_subgrupo = request.GET.get('id_subgrupo')

    try:
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

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Solicitud inválida'}, status=400)


# Vista para crear o actualizar un contratista
def guardar_contratista(request):
    """
    Crea o actualiza un contratista.
    """
    if request.method == 'POST':
        data = request.POST
        id_persona = data.get('id_persona')

        nombre = data.get('nombre')
        telefono = data.get('telefono')
        correo = data.get('correo')
        direccion = data.get('direccion')

        if not nombre or not telefono or not correo:
            return JsonResponse({'error': 'Faltan datos obligatorios'}, status=400)

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    if id_persona:
                        cursor.execute("""
                            UPDATE personas
                            SET primer_nombre = %s, telefono = %s, correo = %s, direccion = %s
                            WHERE id_persona = %s;
                        """, [nombre, telefono, correo, direccion, id_persona])
                    else:
                        cursor.execute("""
                            INSERT INTO personas (primer_nombre, telefono, correo, direccion)
                            VALUES (%s, %s, %s, %s) RETURNING id_persona;
                        """, [nombre, telefono, correo, direccion])
                        id_persona = cursor.fetchone()[0]

                return JsonResponse({'success': True, 'id_persona': id_persona})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Solicitud inválida'}, status=400)


# Vista para listar tablas disponibles
def listado_base(request):
    """
    Muestra la vista unificada con paginación de 50 registros por página.
    """
    with connection.cursor() as cursor:
        # Consulta a la vista_unificada ordenada ascendentemente por id_persona
        query = """
        SELECT *
        FROM vista_unificada
        ORDER BY id_persona ASC;
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    # Configuración de paginación: 50 registros por página
    paginator = Paginator(rows, 50)  
    page = request.GET.get('page', 1)

    try:
        rows_paginated = paginator.page(page)
    except PageNotAnInteger:
        rows_paginated = paginator.page(1)
    except EmptyPage:
        rows_paginated = paginator.page(paginator.num_pages)

    return render(request, 'listado_base.html', {
        'columns': columns,
        'rows': rows_paginated,  # Registros paginados
        'paginator': paginator,  # Objeto paginador para controles avanzados
    })


# Vista para mostrar columnas de una tabla específica
def campos_tabla(request, tabla):
    """
    Devuelve los campos de una tabla específica.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{tabla}';")
            columnas = cursor.fetchall()

        return render(request, 'campos_tabla.html', {'tabla': tabla, 'columnas': columnas})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Vista para consultas dinámicas
def consulta_listado_base(request):
    """
    Permite realizar consultas dinámicas a la base de datos y muestra el resultado.
    """
    resultado = None
    error = None
    message = None

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()

        if not query:
            error = 'La consulta no puede estar vacía.'
        else:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)

                    # Verificamos si hay resultados
                    if query.lower().startswith('select'):
                        columns = [col[0] for col in cursor.description]
                        rows = cursor.fetchall()
                        resultado = {'columns': columns, 'rows': rows}
                    else:
                        # Para operaciones de inserción, actualización o eliminación
                        message = f"{cursor.rowcount} fila(s) afectada(s)."

            except Exception as e:
                error = str(e)

    return render(request, 'consulta_listado_base.html', {
        'resultado': resultado,
        'error': error,
        'message': message,
    })


# Vista para /tablas
def lista_tablas(request):
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
        'supervisores'
    ]
    return render(request, 'lista_tablas.html', {'tablas': tablas})
