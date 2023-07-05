from django.http import HttpResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.models import User
from principal.forms import FormularioContacto, LoginForm, RegistroForm,ActualizarEstadoPedidoForm
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from .models import DetallePedido, Pedido,Producto
from django.views.generic import ListView
from django.db.models import Sum
from django.views import View
from .forms import OPCIONES_ESTADO, AgregarPedidoForm, EliminarPedidoForm, AgregarProductoForm,DireccionClienteForm
from .forms import ProductoForm
from .models import Cliente,  Pedido, DetallePedido,DireccionCliente


# Create your views here.

def home(request):
    return render(request, 'telovendo3app/home.html')

def lista_clientes(request) -> HttpResponse:
    users = User.objects.all()
    return render(request, 'telovendo3app/clientes.html', {'users': users})


class Ingreso(TemplateView):
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, { "form": form })

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('Home')
            form.add_error('username', 'Credenciales incorrectas')
            return render(request, self.template_name, { "form": form })
        else:
            return render(request, self.template_name, { "form": form })


class ListaPedidosView(TemplateView):
    template_name = 'telovendo3app/lista_pedidos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pedidos'] = Pedido.objects.all()
        return context

class AgregarPedidoView(View):
    template_name = 'telovendo3app/agregar_pedido.html'
    form_class = AgregarPedidoForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            cliente = form.cleaned_data['cliente']
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad']
            precio_unitario = form.cleaned_data['precio_unitario']
            
            pedido = Pedido(cliente=cliente, estado='Pendiente', total=0)
            pedido.save()

            detalle_pedido = DetallePedido(pedido=pedido, producto=producto, cantidad=cantidad, precio_unitario=precio_unitario)
            detalle_pedido.subtotal = detalle_pedido.cantidad * detalle_pedido.precio_unitario
            detalle_pedido.save()

            # Actualizar el total del pedido
            pedido.total = DetallePedido.objects.filter(pedido=pedido).aggregate(total=Sum('subtotal'))['total']
            pedido.save()

            # Envío de correo electrónico
            subject = 'Nuevo pedido agregado'
            message = f"Se ha agregado un nuevo pedido.\n\nCliente: {cliente}\nProducto: {producto}\nCantidad: {cantidad}\nPrecio unitario: {precio_unitario}"
            from_email = 'talento@fabricadecodigo.dev'
            to_email = ['arayadiaz.ac@gmail.com'] 
            #to_email = [request.user.email]
            send_mail(subject, message, from_email, to_email)

            return redirect('lista_pedidos')

        return render(request, self.template_name, {'form': form})

class EliminarPedidoView(View):
    template_name = 'telovendo3app/eliminar_pedido.html'

    def get(self, request, pedido_id, *args, **kwargs):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        return render(request, self.template_name, {'pedido': pedido})

    def post(self, request, pedido_id, *args, **kwargs):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        pedido.delete()
        return redirect('lista_pedidos')

class ActualizarEstadoPedidoView(View):
    template_name = 'telovendo3app/editar_estado.html'
    form_class = ActualizarEstadoPedidoForm

    def get(self, request, pedido_id, *args, **kwargs):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        form = self.form_class(instance=pedido)
        opciones_estado = [
            {'valor': 'pendiente', 'etiqueta': 'Pendiente'},
            {'valor': 'en proceso', 'etiqueta': 'En proceso'},
            {'valor': 'enviado', 'etiqueta': 'Enviado'},
            {'valor': 'entregado', 'etiqueta': 'Entregado'},
        ]
        return render(request, self.template_name, {'pedido': pedido, 'form': form, 'opciones_estado': opciones_estado})

    def post(self, request, pedido_id, *args, **kwargs):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        form = self.form_class(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('lista_pedidos')
        

# class ListaProductosView(TemplateView):
#     template_name = 'telovendo3app/lista_productos.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['productos'] = Producto.objects.all()
#         return context
class ListaProductosView(TemplateView):
    template_name = 'telovendo3app/lista_productos.html'
    form_class = AgregarProductoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener los productos disponibles
        productos = Producto.objects.all()
        context['productos'] = productos
        return context

    def post(self, request, *args, **kwargs):
        for producto in Producto.objects.all():
            form = self.form_class(request.POST, prefix=f'producto_{producto.id}')
            if form.is_valid():
                cantidad = form.cleaned_data['cantidad']

                # Obtener o crear el detalle del pedido
                pedido_id = request.session.get('pedido_id')
                if pedido_id:
                    pedido = Pedido.objects.get(id=pedido_id)
                else:
                    pedido = Pedido.objects.create(cliente=request.user, total=0, estado='Pendiente')

                # Asociar el producto al detalle del pedido
                DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)

        return redirect('lista_productos')


class CrearProductoView(TemplateView):
    template_name = 'telovendo3app/crear_producto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProductoForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            print("El formulario es válido")
            form.save()
            return redirect('lista_productos')
        else:
            print("El formulario no es válido")
            context = self.get_context_data(form=form)
            return self.render_to_response(context)


class EditarProductoView(TemplateView):
    template_name = 'telovendo3app/editar_producto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto_id = self.kwargs['producto_id']
        producto = Producto.objects.get(id=producto_id)
        context['form'] = ProductoForm(instance=producto)
        return context

    def post(self, request, *args, **kwargs):
        producto_id = self.kwargs['producto_id']
        producto = Producto.objects.get(id=producto_id)
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
        else:
            context = self.get_context_data(form=form)
            return self.render_to_response(context)


class EliminarProductoView(TemplateView):
    template_name = 'telovendo3app/eliminar_producto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto_id = self.kwargs['producto_id']
        producto = Producto.objects.get(id=producto_id)
        context['producto'] = producto
        return context

    def post(self, request, *args, **kwargs):
        producto_id = self.kwargs['producto_id']
        producto = Producto.objects.get(id=producto_id)
        producto.delete()
        return redirect('lista_productos')
    
class RegistroView(TemplateView):
    template_name = 'registration/registro.html'
    form_class = RegistroForm
    success_url = reverse_lazy('Home')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # Crear instancia de Cliente
            cliente = Cliente.objects.create(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                telefono=form.cleaned_data['telefono']
            )
            cliente.set_password(form.cleaned_data['password1'])
            cliente.save()

            # Autenticar y realizar inicio de sesión
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            user.groups.add(Group.objects.get(name='grupo1'))  # Asignar usuario al grupo "grupo1"
            
            return redirect(self.success_url)

        return render(request, self.template_name, {'form': form})
    

# class AgregarProductoPedidoView(LoginRequiredMixin, TemplateView):
#     template_name = 'telovendo3app/pedido_cliente.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         productos = Producto.objects.filter(disponibilidad__gt=0)
#         productos_with_range = []
#         for producto in productos:
#             producto.disponibilidad_range = range(1, producto.disponibilidad + 1)
#             productos_with_range.append(producto)
#         context['productos'] = productos_with_range
#         return context

#     def post(self, request, *args, **kwargs):
#         pedido, created = Pedido.objects.get_or_create(cliente=request.user, estado='pendiente')
#         producto_id = request.POST.get('producto')
#         cantidad = int(request.POST.get('cantidad'))

#         producto = Producto.objects.get(id=producto_id)
#         if cantidad <= producto.disponibilidad:
#             detalle = DetallePedido(pedido=pedido, producto=producto, cantidad=cantidad, precio_unitario=producto.precio, subtotal=producto.precio * cantidad)
#             detalle.save()

#         return redirect('agregar_producto_pedido')

class AgregarProductoPedidoView(View):
    template_name = 'telovendo3app/pedido_cliente.html'
    form_class = AgregarProductoForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        # Obtener las direcciones del cliente
        direcciones = DireccionCliente.objects.filter(cliente=request.user.cliente)
        
        return render(request, self.template_name, {'form': form, 'direcciones': direcciones})
    
    

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad']

            pedido_id = request.session.get('pedido_id')
            if pedido_id:
                pedido = get_object_or_404(Pedido, id=pedido_id)
            else:
                cliente = request.user.cliente
                pedido = Pedido.objects.create(cliente=cliente,estado='Pendiente', total=0)
                request.session['pedido_id'] = pedido.id

            detalle_pedido = DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad,
                                                          precio_unitario=producto.precio,
                                                          subtotal=producto.precio * cantidad)

            pedido.total += detalle_pedido.subtotal
            pedido.save()

            return redirect('detalles_pedido', pedido_id=pedido.id)

        return render(request, self.template_name, {'form': form})


# class DetallesPedidoView(View):
#     def get(self, request, pedido_id):
#         pedido = get_object_or_404(Pedido, id=pedido_id)
#         detalles = DetallePedido.objects.filter(pedido=pedido)
#         direccion_envio = pedido.direccion_cliente.direccion  # Acceder a la dirección de envío
        
#         context = {
#             'pedido': pedido,
#             'detalles': detalles,
#             'direccion_envio': direccion_envio,
#         }
#         return render(request, 'telovendo3app/detalle_pedido.html', context)
class DetallesPedidoView(View):
    def get(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        detalles = DetallePedido.objects.filter(pedido=pedido)
        context = {
            'pedido': pedido,
            'detalles': detalles,
        }
        return render(request,'telovendo3app/detalle_pedido.html', context)

    def post(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        detalles = DetallePedido.objects.filter(pedido=pedido)
        total = request.POST.get('total')  # Obtener el nuevo total del pedido del formulario

        # Actualizar el total del pedido
        pedido.total = total
        pedido.save()

        context = {
            'pedido': pedido,
            'detalles': detalles,
        }
        return render(request, 'telovendo3app/lista_productos.html', context) #funcionando!!


class SeleccionarDireccionView(View):
    template_name = 'telovendo3app/direcciones_cliente.html'

    def get(self, request, *args, **kwargs):
        cliente = request.user.cliente
        direcciones = DireccionCliente.objects.filter(cliente=cliente)
        return render(request, self.template_name, {'direcciones': direcciones})

    def post(self, request, *args, **kwargs):
        direccion_id = request.POST.get('direccion_id')
        if direccion_id:
            direccion = get_object_or_404(DireccionCliente, id=direccion_id)
            request.session['direccion_envio'] = direccion.direccion
        return redirect('agregar_producto_pedido')
    
class DireccionClienteView(View):
    template_name = 'telovendo3app/agregar_direccion.html'
    form_class = DireccionClienteForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            direccion = form.cleaned_data['direccion']
            cliente = request.user.cliente
            DireccionCliente.objects.create(cliente=cliente, direccion=direccion)
            return redirect('lista_productos')

        return render(request, self.template_name, {'form': form})

class CrearPedidoView(TemplateView):
    template_name = 'telovendo3app/crear_pedido.html'
    form_class = DireccionClienteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener las direcciones del cliente actual
        direcciones = DireccionCliente.objects.filter(cliente=self.request.user)
        context['direcciones'] = direcciones
        return context

    def post(self, request, *args, **kwargs):
        # Obtener la dirección seleccionada
        direccion_id = request.POST.get('direccion_cliente')

        if direccion_id:
            direccion = DireccionCliente.objects.get(id=direccion_id)
        else:
            # Crear una nueva dirección si no se selecciona ninguna existente
            direccion = DireccionCliente.objects.create(
                cliente=Cliente.objects.get(username=request.user.username),
                direccion='direccion'  # Reemplaza 'direccion' con el valor deseado
            )

        # Crear el pedido
        pedido = Pedido.objects.create(
            cliente=Cliente.objects.get(username=request.user.username),
            direccion_cliente=direccion,
            total=0,
            estado='Pendiente'  # Agrega el estado correcto para el pedido
        )

        # Establecer la sesión del pedido del cliente
        request.session['pedido_id'] = pedido.id #ta listo

        return redirect('lista_productos')


    