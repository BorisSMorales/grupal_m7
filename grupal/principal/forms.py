from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cliente, Producto,Pedido

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

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class AgregarPedidoForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all())
    producto = forms.ModelChoiceField(queryset=Producto.objects.all())
    cantidad = forms.IntegerField()
    precio_unitario = forms.DecimalField(decimal_places=2)

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