from django.db import models
from django.contrib.auth.models import User

class ValidacionTri(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    consecutivo = models.CharField(max_length=15)
    referencia = models.CharField(max_length=15)
    descripcion = models.CharField(max_length=100)
    bodega = models.CharField(max_length=100)
    extension = models.CharField(max_length=100)
    unidad_medida = models.CharField(max_length=15)
    cantidad = models.IntegerField()
    ubicacion = models.CharField(max_length=100)
    
    validacion_descripcion = models.CharField(max_length=50)
    validacion_cantidad = models.CharField(max_length=50)
    validacion_proveedor = models.CharField(max_length=50)
    validacion_marcacion = models.CharField(max_length=50)
    validacion_fecha_tri = models.CharField(max_length=50)
    validacion_sello = models.CharField(max_length=50)
    validacion_firma_almacen = models.CharField(max_length=50)
    validacion_firma_proveedor = models.CharField(max_length=50)
    evidencia_tri = models.ImageField(upload_to='validacionTri/')
    vigilante = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "validacion_tri"
        
        

class ValidacionLlantas(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    consecutivo = models.CharField(max_length=15)
    referencia = models.CharField(max_length=15)
    descripcion = models.CharField(max_length=100)
    bodega = models.CharField(max_length=100)
    extension = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)
    serial = models.CharField(max_length=100)
    quemado = models.CharField(max_length=100)
    vin = models.CharField(max_length=100)
    
    validacion_descripcion = models.CharField(max_length=50)
    validacion_serial = models.CharField(max_length=50)
    validacion_quemado = models.CharField(max_length=50)
    validacion_vin = models.CharField(max_length=50)
    validacion_proveedor = models.CharField(max_length=50)
    validacion_fecha_llantas = models.CharField(max_length=50)
    validacion_documento_anexo = models.CharField(max_length=50)
    validacion_sello = models.CharField(max_length=50)
    validacion_firma_almacen = models.CharField(max_length=50)
    validacion_firma_proveedor = models.CharField(max_length=50)
    vigilante = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "validacion_llantas"




class EvidenciaTris(models.Model):
    tipo = models.CharField(max_length=50) 
    ruta = models.FileField(upload_to='evidenciasTris/')
    fecha = models.DateField()
    tri = models.ForeignKey(ValidacionTri, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "evidenciaTris"



class EvidenciaLlantas(models.Model):
    tipo = models.CharField(max_length=50) 
    ruta = models.FileField(upload_to='evidenciasLlantas/')
    fecha = models.DateField()
    llanta = models.ForeignKey(ValidacionLlantas, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "evidenciaLlantas"





class ValidacionManual(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    numero_manual = models.CharField(max_length=100)
    ruta_imagen = models.ImageField(upload_to='validacionManual/')
    motivo_retiro = models.CharField(max_length=50)
    concepto_salida = models.CharField(max_length=50)
    validacion_sello = models.CharField(max_length=50)
    validacion_tachones_enmendaduras = models.CharField(max_length=50)
    validacion_firma_almacen = models.CharField(max_length=50)
    validacion_firma_autorizacion = models.CharField(max_length=50)
    validacion_firma_proveedor = models.CharField(max_length=50)
    
    vigilante = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "validacion_manual"

    def __str__(self):
        return f"{self.numero_manual} - {self.usuario.username}"