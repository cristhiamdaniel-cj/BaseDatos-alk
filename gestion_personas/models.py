from django.db import models

class Persona(models.Model):
    id_persona = models.AutoField(primary_key=True)  # Define id_persona como clave primaria
    apellido_paterno = models.CharField(max_length=255)
    apellido_materno = models.CharField(max_length=255, blank=True, null=True)
    primer_nombre = models.CharField(max_length=255)
    segundo_nombre = models.CharField(max_length=255, blank=True, null=True)
    genero = models.CharField(max_length=50)
    telefono = models.CharField(max_length=50)
    correo = models.EmailField(unique=True)
    direccion = models.CharField(max_length=255)

    class Meta:
        db_table = 'personas'  # Apunta a la tabla existente
