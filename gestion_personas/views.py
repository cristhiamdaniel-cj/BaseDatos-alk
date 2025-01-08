from django.shortcuts import render, redirect, get_object_or_404
from .models import Persona
from django.db import connection

# Lista de personas
def lista_personas(request):
    personas = Persona.objects.all()
    return render(request, 'lista_personas.html', {'personas': personas})


def consulta_sql(request):
    resultado = []
    error = None

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()

        if query:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    if query.lower().startswith('select'):
                        # Obtener nombres de columnas y filas de resultados
                        columns = [col[0] for col in cursor.description]
                        resultado = {
                            'columns': columns,
                            'rows': cursor.fetchall(),
                        }
                    else:
                        resultado = f"Consulta ejecutada correctamente: {cursor.rowcount} filas afectadas."
            except Exception as e:
                error = str(e)
        else:
            error = "No se puede ejecutar una consulta vacía."

    return render(request, 'consulta_sql.html', {'resultado': resultado, 'error': error})


# Agregar una persona
def agregar_persona(request):
    if request.method == 'POST':
        primer_nombre = request.POST['primer_nombre']
        segundo_nombre = request.POST.get('segundo_nombre', '')
        apellido_paterno = request.POST['apellido_paterno']
        apellido_materno = request.POST.get('apellido_materno', '')
        genero = request.POST['genero']
        telefono = request.POST['telefono']
        correo = request.POST['correo']
        direccion = request.POST['direccion']

        Persona.objects.create(
            primer_nombre=primer_nombre,
            segundo_nombre=segundo_nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            genero=genero,
            telefono=telefono,
            correo=correo,
            direccion=direccion
        )
        return redirect('lista_personas')

    return render(request, 'agregar_persona.html')

# Editar una persona
def editar_persona(request, id):
    persona = get_object_or_404(Persona, pk=id)

    if request.method == 'POST':
        persona.primer_nombre = request.POST['primer_nombre']
        persona.segundo_nombre = request.POST['segundo_nombre']
        persona.apellido_paterno = request.POST['apellido_paterno']
        persona.apellido_materno = request.POST['apellido_materno']
        persona.genero = request.POST['genero']
        persona.telefono = request.POST['telefono']
        persona.correo = request.POST['correo']
        persona.direccion = request.POST['direccion']
        persona.save()
        return redirect('lista_personas')

    return render(request, 'editar_persona.html', {'persona': persona})

# Eliminar una persona
def eliminar_persona(request, id):
    persona = get_object_or_404(Persona, pk=id)
    persona.delete()
    return redirect('lista_personas')
