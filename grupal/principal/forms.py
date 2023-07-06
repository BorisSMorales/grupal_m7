from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Cliente, Producto,Pedido,DireccionCliente, DetallePedido

class FormularioContacto(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=50, required=True,
                            widget=forms.TextInput(attrs={'placeholder': 'Ingrese su Nombre', 'class': 'form-control'}),
                            error_messages={'required':'El nombre es obligatorio', 'max_length': 'el nombre no puede tener más de 50 caracteres'})
    email = forms.EmailField(label="Email", max_length=100,min_length=5, required=True,
                            widget=forms.TextInput(attrs={'placeholder': 'Ingrese su Email', 'class': 'form-control'}),
                            error_messages={'required':'El Email es obligatorio', 'max_length':'el email no puede tener más de 100 caracteres','min_length': 'El email debe tener al menos 5 caracteres'})
    empresa = forms.CharField(label='Empresa', max_length=100, required=True,
                            widget=forms.TextInput(attrs={'placeholder':'Ingrese el nombre de la Empresa que representa', 'class':'form-control'}),
                            error_messages= {'required':'El nombre de la empresa es obligatorio', 'max_lenght':'El nombre de la empresa es muy largo'})
    asunto = forms.CharField(label='Asunto', max_length=100, required=True,
                            widget=forms.TextInput(attrs={'placeholder':'Ingrese el Asunto de su mensaje', 'class':'form-control'}),
                            error_messages= {'required':'El asunto es obligatorio', 'max_lenght':'El asunto no debe tener mas de 100 caracteres'})
    mensaje = forms.CharField(label ='Mensaje', max_length=1000, required = True,
                            widget=forms.Textarea(attrs={'placeholder':'Ingrese su mensaje, en no mas de 1000 caracteres', 'class':'form-control'}),
                            error_messages= {'required':'El mensaje es obligatorio', 'max_length':'El maximo de caracteres es de 1000'})

class LoginForm(forms.Form):
    username = forms.CharField(label='Usuario', required=True,
                                max_length=50, min_length=5,
                                error_messages={
                                    'required': 'El usuario es obligatorio',
                                    'max_length': 'El usuario no puede superar los 50 caracteres',
                                    'min_length': 'El usuario debe tener al menos 5 caracteres'
                                },
                                widget=forms.TextInput(attrs={
                                    'placeholder': 'Ingrese su usuario',
                                    'class': 'form-control'
                                })
                                )
    password = forms.CharField(label='Contraseña', required=True,
                                max_length=50, min_length=1,
                                error_messages={
                                    'required': 'La contraseña es obligatoria',
                                    'max_length': 'La contraseña no puede superar los 50 caracteres',
                                    'min_length': 'La contraseña debe tener al menos 1 caracter'
                                },
                                widget=forms.PasswordInput(attrs={
                                    'placeholder': 'Ingrese su contraseña',
                                    'class': 'form-control'
                                })
                                )

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    telefono = forms.CharField(max_length=20, required=True)  # Agregar campo telefono

    class Meta:
        model = Cliente
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'password1', 'password2')

class AgregarPedidoForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all())
    producto = forms.ModelChoiceField(queryset=Producto.objects.all())
    cantidad = forms.IntegerField()
    precio_unitario = forms.DecimalField(decimal_places=2)
    direccion = forms.ModelChoiceField(queryset=DireccionCliente.objects.all(), empty_label=None)

    def save(self):
        cliente = self.cleaned_data['cliente']
        producto = self.cleaned_data['producto']
        cantidad = self.cleaned_data['cantidad']
        precio_unitario = self.cleaned_data['precio_unitario']
        direccion_cliente = self.cleaned_data['direccion']

        pedido = Pedido(cliente=cliente, direccion_cliente=direccion_cliente, estado='Pendiente', total=0)
        pedido.save()

        detalle_pedido = DetallePedido(pedido=pedido, producto=producto, cantidad=cantidad, precio_unitario=precio_unitario)
        detalle_pedido.subtotal = detalle_pedido.cantidad * detalle_pedido.precio_unitario
        detalle_pedido.save()


class EliminarPedidoForm(forms.Form):
    confirmacion = forms.BooleanField(required=True)


OPCIONES_ESTADO = [
    ('pendiente', 'Pendiente'),
    ('procesando', 'En proceso'),
    ('enviado', 'Enviado'),
    ('entregado', 'Entregado'),
]

class ActualizarEstadoPedidoForm(forms.ModelForm):
    estado = forms.ChoiceField(choices=OPCIONES_ESTADO)
    
    class Meta:
        model = Pedido
        fields = ['estado']

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'precio', 'disponibilidad', 'descripcion']

    

class AgregarProductoForm(forms.Form):
    producto = forms.ModelChoiceField(queryset=Producto.objects.filter(disponibilidad__gt=0))
    cantidad = forms.IntegerField(min_value=1, max_value=10)

# class AgregarProductoForm(forms.Form):
#     producto = forms.ModelChoic|eField(queryset=Producto.objects.all())
#     cantidad = forms.IntegerField()

#     def __init__(self, *args, **kwargs):
#         cantidades_disponibles = kwargs.pop('cantidades_disponibles')
#         super().__init__(*args, **kwargs)
#         self.fields['cantidad'].widget = forms.Select(choices=[(cantidad, cantidad) for cantidad in cantidades_disponibles])

class DireccionClienteForm(forms.ModelForm):
    class Meta:
        model = DireccionCliente
        fields = ['direccion']