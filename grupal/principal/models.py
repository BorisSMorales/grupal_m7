from django.db import models
from django.contrib.auth.models import AbstractUser, User
from PIL import Image

# Create your models here.


# class Cliente(models.Model):
#     nombre = models.CharField(max_length=100,null=False,blank=False)
#     telefono = models.CharField(max_length=20,null=False,blank=False)
#     correo_electronico = models.EmailField(max_length=100,null=False,blank=False)

#     def __str__(self):
#         return self.nombre


class Cliente(User):
    telefono = models.CharField(max_length=20, null=False, blank=False)
    nombre = models.CharField(max_length=100, null=False, blank=False)
    correo_electronico = models.EmailField(max_length=100, null=False, blank=False)

    def save(self, *args, **kwargs):
        self.telefono = self.telefono
        self.nombre = self.username  # Asignar el valor de username a nombre
        self.correo_electronico = self.email  # Asignar el valor de email a correo_electronico
        super().save(*args, **kwargs)  # Llamar al método save() de la clase padre

    def str(self):
        return self.username

# class Cliente(AbstractUser):
#     telefono = models.CharField(max_length=20, null=False, blank=False)

#     def str(self):
#         return self.username

class DireccionCliente(models.Model):
    cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE)
    direccion = models.CharField(max_length=200,null=False, blank=False)

    def __str__(self):
        return self.direccion
    
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100,null=False,blank=False)
    descripcion = models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100, null=False,blank=False)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    precio = models.IntegerField(null=False,blank=False)
    disponibilidad = models.IntegerField(null=False,blank=False)
    descripcion = models.CharField(max_length=200,null=True,blank=True)
    imagen = models.ImageField(upload_to='imagen_productos', null=True)

    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.imagen:
            img = Image.open(self.imagen.path)

            tamano_deseado = (225, 225)

            img.thumbnail(tamano_deseado)
            
            img.save(self.imagen.path)



class Pedido(models.Model):
    fecha_pedido = models.DateField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    direccion_cliente = models.ForeignKey(DireccionCliente, on_delete=models.SET_NULL, null=True) 
    total = models.DecimalField(max_digits=10, decimal_places=2,null=False,blank=False)
    estado = models.CharField(max_length=50,null=False,blank=False)


    def __str__(self):
        return f"Pedido #{self.id}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2,null=False,blank=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2,null=False,blank=False)
