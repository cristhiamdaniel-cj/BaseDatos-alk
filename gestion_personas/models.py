from django.db import models
from django.core.exceptions import ValidationError


# Validación personalizada para valores positivos
def validate_positive(value):
    if value <= 0:
        raise ValidationError(f'El valor {value} debe ser positivo.')


class Area(models.Model):
    id_area = models.AutoField(primary_key=True)
    nombre_area = models.CharField(max_length=255)

    class Meta:
        db_table = 'areas'
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'

    def __str__(self):
        return self.nombre_area


class Subgrupo(models.Model):
    id_subgrupo = models.AutoField(primary_key=True)
    nombre_subgrupo = models.CharField(max_length=255)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='subgrupos')

    class Meta:
        db_table = 'subgrupos'
        verbose_name = 'Subgrupo'
        verbose_name_plural = 'Subgrupos'

    def __str__(self):
        return self.nombre_subgrupo


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=255)
    subgrupo = models.ForeignKey(Subgrupo, on_delete=models.CASCADE, related_name='roles')

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre_rol


class Persona(models.Model):
    id_persona = models.AutoField(primary_key=True)  # Clave primaria autoincremental
    apellido_paterno = models.CharField(max_length=255)
    apellido_materno = models.CharField(max_length=255, blank=True, null=True)
    primer_nombre = models.CharField(max_length=255)
    segundo_nombre = models.CharField(max_length=255, blank=True, null=True)

    # Opciones predefinidas para género
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    telefono = models.CharField(max_length=50)
    correo = models.EmailField(unique=True)
    direccion = models.CharField(max_length=255)

    # Relación con Rol
    id_rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='personas')

    class Meta:
        db_table = 'personas'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    def __str__(self):
        return f"{self.primer_nombre} {self.apellido_paterno}"


class Identificacion(models.Model):
    id_identificacion = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='identificaciones')
    numero_identificacion = models.BigIntegerField(unique=True, validators=[validate_positive])
    lugar_expedicion = models.CharField(max_length=255)

    # Opciones para tipo de identificación
    TIPO_IDENTIFICACION_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('PA', 'Pasaporte'),
        ('CE', 'Cédula de Extranjería'),
    ]
    tipo_identificacion = models.CharField(max_length=2, choices=TIPO_IDENTIFICACION_CHOICES, default='CC')

    class Meta:
        db_table = 'identificacion'
        verbose_name = 'Identificación'
        verbose_name_plural = 'Identificaciones'

    def __str__(self):
        return f"{self.numero_identificacion} - {self.lugar_expedicion}"


class Contrato(models.Model):
    id_contrato = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='contratos')
    numero_contrato = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    meses_antiguedad = models.IntegerField(validators=[validate_positive])
    honorarios_mes = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_positive])
    objeto_contrato = models.TextField()
    numero_obligaciones = models.IntegerField(validators=[validate_positive])

    class Meta:
        db_table = 'contratos'
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'

    def __str__(self):
        return self.numero_contrato


class ProcesoContractual(models.Model):
    id_proceso = models.AutoField(primary_key=True)
    numero_sipse = models.CharField(max_length=255)
    fecha_de_solicitud = models.DateField()
    fecha_de_vencimiento = models.DateField()
    abogado_a_cargo = models.CharField(max_length=255)
    cdp = models.CharField(max_length=255)
    crp = models.CharField(max_length=255)
    numero_de_no_hay = models.CharField(max_length=255)
    riesgo = models.SmallIntegerField()

    class Meta:
        db_table = 'proceso_contractual'
        verbose_name = 'Proceso Contractual'
        verbose_name_plural = 'Procesos Contractuales'

    def __str__(self):
        return self.numero_sipse


class ProcesoPersona(models.Model):
    id_proceso = models.ForeignKey(ProcesoContractual, on_delete=models.CASCADE, related_name='procesos_personas')
    id_persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='procesos_personas')

    class Meta:
        db_table = 'proceso_personas'
        verbose_name = 'Proceso Persona'
        verbose_name_plural = 'Procesos Personas'

    def __str__(self):
        return f"Proceso: {self.id_proceso} - Persona: {self.id_persona}"

