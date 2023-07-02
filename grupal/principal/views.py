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
from .forms import OPCIONES_ESTADO, AgregarPedidoForm, EliminarPedidoForm
from .forms import ProductoForm


# Create your views here.

def home(request):
    return render(request, 'telovendo3app/home.html')

def lista_clientes(request) -> HttpResponse:
    users = User.objects.all()
    return render(request, 'telovendo3app/clientes.html', {'users': users})

def Registro(request):
    return render(request, 'registration/registro.html')




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
        

class ListaProductosView(TemplateView):
    template_name = 'telovendo3app/lista_productos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.all()
        return context


class CrearProductoView(TemplateView):
    template_name = 'telovendo3app/crear_producto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProductoForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
        else:
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