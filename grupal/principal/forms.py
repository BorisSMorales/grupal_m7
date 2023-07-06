from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cliente, Producto,Pedido,DireccionCliente, DetallePedido
from django.forms.models import inlineformset_factory

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

class DireccionClienteForm(forms.ModelForm):
    class Meta:
        model = DireccionCliente
        fields = ['direccion']

class FormSeleccionarCliente(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all())

class FormPedidogestion(forms.ModelForm):
    OPCIONES_ESTADO = [('Pendiente', 'Pendiente'), ('Procesando', 'En Proceso'), ('Enviado', 'Enviado'), ('Entregado', 'Entregado')]

    direccion_cliente = forms.ModelChoiceField(queryset=DireccionCliente.objects.none(), required=True)
    total = forms.DecimalField(label='Total', required=True, error_messages={'required': 'El total es requerido'}, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total'}), help_text='Ingrese el total')
    estado = forms.ChoiceField(choices=OPCIONES_ESTADO, required=True, error_messages={'required': 'El estado es requerido'}, widget=forms.Select(attrs={'class': 'form-control'}), help_text='Seleccione el estado del pedido')

    class Meta:
        model = Pedido
        fields = ['direccion_cliente', 'total', 'estado']

    def __init__(self, cliente_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cliente_id:
            cliente = Cliente.objects.get(id=cliente_id)
            self.fields['direccion_cliente'].queryset = cliente.direccioncliente_set.all()

class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio_unitario']

    def __init__(self, pedido_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pedido_id = pedido_id

    def save(self, commit=True):
        detalle_pedido = super().save(commit=False)
        detalle_pedido.pedido_id = self.pedido_id
        detalle_pedido.subtotal = detalle_pedido.cantidad * detalle_pedido.precio_unitario
        if commit:
            detalle_pedido.save()
        return detalle_pedido



