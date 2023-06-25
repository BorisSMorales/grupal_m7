from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from principal.forms import FormularioContacto, LoginForm, RegistroForm
from django.views.generic import TemplateView
from principal.models import Contacto
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.contrib.auth.models import Group

# Create your views here.

def home(request):
    return render(request, 'telovendo3app/base.html')

def lista_clientes(request) -> HttpResponse:
    users = User.objects.all()
    return render(request, 'telovendo3app/clientes.html', {'users': users})

class ContactoView(TemplateView):
    template_name = 'telovendo3app/contacto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formulario'] = FormularioContacto()
        return context

    def post(self, request, *args, **kwargs):
        form = FormularioContacto(request.POST)
        mensajes = {
            "enviado": False,
            "resultado": None
        }
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            empresa = form.cleaned_data['empresa']
            asunto = form.cleaned_data['asunto']
            mensaje = form.cleaned_data['mensaje']

            registro = Contacto(
                nombre=nombre,
                email=email,
                empresa=empresa,
                asunto=asunto,
                mensaje=mensaje
            )
            registro.save()

            mensajes = { "enviado": True, "resultado": "Mensaje enviado correctamente" }
        else:
            mensajes = { "enviado": False, "resultado": form.errors }
        return render(request, self.template_name, { "formulario": form, "mensajes": mensajes })
    
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

class RegistroView(TemplateView):
    template_name = 'registration/registro.html'
    form_class = RegistroForm
    success_url = reverse_lazy('Home')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            user.groups.add(Group.objects.get(name='grupo1'))  # Asignar usuario al grupo "grupo1"
            
            return redirect(self.success_url)
            

        return render(request, self.template_name, {'form': form})    