from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.views import View
from principal.forms import FormularioContacto, LoginForm, RegistroForm, AgregarPedidoForm
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from .models import DetallePedido, Pedido,Producto
from django.views.generic import ListView
from django.db.models import Sum


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

            pedido.total = DetallePedido.objects.filter(pedido=pedido).aggregate(total=Sum('subtotal'))['total']
            pedido.save()

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