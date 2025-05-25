from django.db import models
from django.contrib.auth.models import User

class ValidacionTri(models.Model):
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    consecutivo = models.CharField(max_length=15)
    referencia = models.CharField(max_length=15)
    descripcion = models.CharField(max_length=100)
    bodega = models.CharField(max_length=100)
    extension = models.CharField(max_length=100)
    unidad_medida = models.CharField(max_length=15)
    cantidad = models.IntegerField()
    ubicacion = models.CharField(max_length=100)
    validacion = models.CharField(max_length=800)
    vigilante = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "validacion_tri"
        
        

class ValidacionManual(models.Model):
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    numero_manual = models.CharField(max_length=100)
    ruta_imagen = models.ImageField(upload_to='validacionManual/')
    vigilante = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "validacion_manual"

    def __str__(self):
        return f"{self.numero_manual} - {self.usuario.username}"