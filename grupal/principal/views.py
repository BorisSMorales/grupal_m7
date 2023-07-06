from django.http import HttpResponse
from django.shortcuts import redirect, render,get_object_or_404, reverse
from django.core.mail import send_mail
from django.contrib.auth.models import User
from principal.forms import FormularioContacto, LoginForm, RegistroForm,ActualizarEstadoPedidoForm
from django.views.generic import TemplateView
from django.views.generic import FormView

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import Group
from .models import DetallePedido, Pedido,Producto, Cliente
from django.views.generic import ListView
from django.db.models import Sum
from django.views import View
from .forms import OPCIONES_ESTADO, EliminarPedidoForm, ProductoForm, DetallePedidoForm, FormPedidogestion, FormSeleccionarCliente
from .models import DireccionCliente
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView



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
    
class RegistroView(TemplateView):
    template_name = 'registration/registro.html'
    form_class = RegistroForm
    success_url = reverse_lazy('Home')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # Crear instancia de Cliente
            cliente = Cliente(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                telefono=form.cleaned_data['telefono'],  # Obtener valor de telefono
            )
            cliente.set_password(form.cleaned_data['password1'])
            cliente.save()

            # Autenticar y realizar inicio de sesión
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)

            return redirect(self.success_url)

        return render(request, self.template_name, {'form': form})
    
# class GestionPedidoView(TemplateView):
#     template_name = 'agregar_pedido.html'
#     form_class = DireccionClienteForm


class SeleccionarClienteView(View):
    template_name = 'telovendo3app/seleccionar_cliente.html'
    form_class = FormSeleccionarCliente

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        cliente_id = request.POST.get('cliente')
        return redirect('agregar_pedido', cliente_id=int(cliente_id))

class PedidoGestionView(FormView):
    template_name = 'telovendo3app/agregar_pedido.html'
    form_class = FormPedidogestion

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['cliente_id'] = int(self.kwargs['cliente_id'])
        return kwargs
      
    def form_valid(self, form):
        pedido = form.save(commit=False)
        pedido.cliente_id = self.kwargs['cliente_id']
        pedido.save()

        return redirect('detalle_pedido', pedido_id=pedido.id)
    
class DetallePedidoView(View):
    template_name = 'telovendo3app/detalle_pedido.html'

    def get(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        detalles = DetallePedido.objects.filter(pedido=pedido)
        return render(request, self.template_name, {'pedido': pedido, 'detalles': detalles})
    
class AgregarDetallePedidoView(FormView):
    template_name = 'telovendo3app/agregar_detalle_pedido.html'
    form_class = DetallePedidoForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pedido_id'] = int(self.kwargs['pedido_id'])
        return kwargs

    def form_valid(self, form):
        detalle_pedido = form.save(commit=False)
        detalle_pedido.pedido_id = self.kwargs['pedido_id']
        detalle_pedido.subtotal = detalle_pedido.cantidad * detalle_pedido.precio_unitario
        detalle_pedido.save()

        return redirect('detalle_pedido', pedido_id=detalle_pedido.pedido_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detalle_form'] = context['form']
        return context