from django.db import models

# Create your models here.


class Cliente(models.Model):
    nombre = models.CharField(max_length=100,null=False,blank=False)
    telefono = models.CharField(max_length=20,null=False,blank=False)
    correo_electronico = models.EmailField(max_length=100,null=False,blank=False)

    def __str__(self):
        return self.nombre


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
    precio = models.IntegerField(max_digits=10, null=False,blank=False)
    disponibilidad = models.IntegerField(null=False,blank=False)
    descripcion = models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return self.nombr


class Pedido(models.Model):
    fecha_pedido = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2,null=False,blank=False)

    def __str__(self):
        return f"Pedido #{self.id}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2,null=False,blank=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2,null=False,blank=False)
    estado = models.CharField(max_length=50,null=False,blank=False)
