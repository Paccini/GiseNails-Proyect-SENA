from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from empleados.models import Empleado
from servicio.models import Servicio
from clientes.models import Cliente
from .forms import ReservaForm, ReservaEditForm
from reserva.models import HorarioDisponible, Reserva
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from django.utils import timezone
from productos.models import Producto
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Reserva, PagoReserva
from .forms import PagoReservaForm
from datetime import datetime, time, timedelta
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from django import forms
from django.utils.formats import number_format, localize

class ReferenciaPagoForm(forms.Form):
    metodo = forms.ChoiceField(choices=[('nequi', 'Nequi'), ('daviplata', 'Daviplata')], widget=forms.Select(attrs={'class': 'form-select'}))
    referencia = forms.CharField(label='Referencia de pago', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de referencia'}))

def reserva(request):
    gestoras = Empleado.objects.all()
    horarios = HorarioDisponible.objects.all()
    servicios = Servicio.objects.all()
    # Agrupa servicios por categoría
    servicios_por_categoria = {
        'manicure': servicios.filter(categoria='manicure'),
        'pedicure': servicios.filter(categoria='pedicure'),
        'estructura': servicios.filter(categoria='estructura'),
    }

    if request.method == "POST":
        try:
            gestora_id = request.POST.get("gestora")
            nombre_cliente = request.POST.get("nombre")
            telefono_cliente = request.POST.get("telefono")
            servicio_id = request.POST.get("servicio")
            hora_id = request.POST.get("hora")
            fecha_str = request.POST.get("fecha")
            correo_cliente = request.POST.get("correo")

            # Validaciones básicas: asegurar que los ids existen
            if not gestora_id or not servicio_id or not hora_id:
                return JsonResponse({"success": False, "error": "Selecciona gestora, servicio y horario."})

            try:
                gestora = Empleado.objects.get(id=gestora_id)
            except Empleado.DoesNotExist:
                return JsonResponse({"success": False, "error": "Gestora no encontrada."})

            try:
                servicio = Servicio.objects.get(id=servicio_id)
            except Servicio.DoesNotExist:
                return JsonResponse({"success": False, "error": "Servicio no encontrado."})

            try:
                hora = HorarioDisponible.objects.get(id=hora_id)
            except HorarioDisponible.DoesNotExist:
                return JsonResponse({"success": False, "error": "Horario no disponible (selecciona otro)."})

            # parsear fecha (se espera formato d/m/Y desde flatpickr)
            from datetime import datetime
            try:
                fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
            except Exception:
                # intentar ISO (Y-m-d)
                fecha = datetime.fromisoformat(fecha_str).date()

            # Preparar datos de reserva para guardarlos en sesión y completar tras login/registro
            pending = {
                'gestora_id': gestora.id,
                'servicio_id': servicio.id,
                'hora_id': hora.id,
                'fecha': fecha.strftime('%Y-%m-%d'),
                'nombre': nombre_cliente,
                'telefono': telefono_cliente,
                'correo': correo_cliente,
            }

            # comprobar si el correo ya existe en clientes
            from clientes.models import Cliente
            cliente_obj = Cliente.objects.filter(correo__iexact=correo_cliente).first()
            request.session['pending_reserva'] = pending

            if cliente_obj:
                # ya existe: pedir login (solo contraseña)
                from django.urls import reverse
                login_url = reverse('login:login')
                return JsonResponse({"next": f"{login_url}?next=/completar-reserva/", "need": "login"})
            else:
                # no existe: redirigir al login mostrando el panel de registro
                from django.urls import reverse
                registro_url = reverse('login:login')
                return JsonResponse({"next": f"{registro_url}?register_active=true&next=/completar-reserva/", "need": "register"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    # Eliminar la reserva pendiente si el usuario cambia de vista
    if 'pending_reserva' in request.session:
        del request.session['pending_reserva']

    return render(request, 'reservas/reserva.html', {
        'gestoras': gestoras,
        'horarios': horarios,
        'servicios_por_categoria': servicios_por_categoria,
    })

def horarios_disponibles(request):
    fecha = request.GET.get('fecha')
    gestora_id = request.GET.get('gestora_id')
    horarios = HorarioDisponible.objects.all()
    from datetime import datetime
    try:
        fecha_obj = datetime.strptime(fecha, '%d/%m/%Y').date()
    except Exception:
        return JsonResponse({'horarios': []})

    ocupados_qs = Reserva.objects.filter(fecha=fecha_obj)
    if gestora_id:
        ocupados_qs = ocupados_qs.filter(gestora_id=gestora_id)
    ocupados = ocupados_qs.values_list('hora_id', flat=True)
    disponibles = horarios.exclude(id__in=ocupados)

    horarios_data = []
    now = timezone.localtime().time()
    es_hoy = fecha_obj == timezone.localdate()
    for h in disponibles:
        hora_str = h.hora.strftime('%H:%M')
        disabled = False
        if es_hoy and h.hora <= now:
            disabled = True
        horarios_data.append({
            'id': h.id,
            'hora': hora_str,
            'disabled': disabled
        })
    return JsonResponse({'horarios': horarios_data})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def home(request):
    ahora = timezone.localtime()
    hoy = ahora.date()
    hora_actual = ahora.time().replace(second=0, microsecond=0)

    # Cancelar solo las pendientes cuya fecha es menor a hoy
    Reserva.objects.filter(
        estado='pendiente',
        fecha__lt=hoy
    ).update(estado='cancelada')

    # Cancelar solo las pendientes de hoy cuya hora ya pasó
    Reserva.objects.filter(
        estado='pendiente',
        fecha=hoy,
        hora__hora__lt=hora_actual
    ).update(estado='cancelada')

    # CANCELAR LAS CITAS PENDIENTES QUE NO HAN SIDO CONFIRMADAS UN DÍA ANTES
    plazo = hoy + timedelta(days=1)
    Reserva.objects.filter(
        estado='pendiente',
        fecha__lte=plazo
    ).update(estado='cancelada')

    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    usuario = request.GET.get('usuario', '')
    estado = request.GET.get('estado', '')
    referencia = request.GET.get('referencia', '').strip()

    citas = Reserva.objects.all()
    # Excluye canceladas y realizadas por defecto
    if not estado:
        citas = citas.exclude(estado__in=['realizada', 'cancelada'])
    else:
        citas = citas.filter(estado=estado)

    # Filtrar por rango de fechas
    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            citas = citas.filter(fecha__gte=fecha_inicio_obj)
        except Exception:
            pass
    
    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            citas = citas.filter(fecha__lte=fecha_fin_obj)
        except Exception:
            pass
    
    if usuario:
        citas = citas.filter(cliente__nombre__icontains=usuario)

    if referencia:
        citas = citas.filter(pagos__referencia__icontains=referencia)

    citas = citas.order_by('fecha', 'hora__hora')

    paginator = Paginator(citas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'reservas': page_obj,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'usuario': usuario,
        'estado': estado,
        'referencia': referencia,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'reservas/home.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def agregar_reserva(request):
    fecha = request.GET.get('fecha')
    gestora = request.GET.get('gestora')
    form = ReservaForm(request.POST or None)

    # Filtra las horas solo si hay fecha y gestora seleccionadas
    if fecha and gestora:
        ocupadas = Reserva.objects.filter(
            gestora_id=gestora,
            fecha=fecha
        ).values_list('hora_id', flat=True)
        horas_disponibles = HorarioDisponible.objects.exclude(id__in=ocupadas)
        form.fields['hora'].queryset = horas_disponibles.order_by('hora')
    else:
        form.fields['hora'].queryset = HorarioDisponible.objects.all().order_by('hora')

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('reserva:home')

    return render(request, 'reservas/agregar.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def editar_reserva(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Reserva.ESTADO_CHOICES):
            cita.estado = nuevo_estado
            cita.save()
            messages.success(request, "Estado actualizado correctamente.")
            return redirect('reserva:home')
    else:
        form = ReservaEditForm(instance=cita)
    context = {'form': form}
    return render(request, 'reservas/editar.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
@never_cache
def eliminar_reserva(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        cita.delete()
        return redirect("reserva:home")
    return render(request, 'reservas/eliminar.html', {'cita': cita})


class ReservaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/agregar.html'
    success_url = reverse_lazy('reserva:home')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        # El formulario ya tiene el cliente seleccionado
        self.object = form.save()
        return super().form_valid(form)

@login_required
def completar_reserva(request):
    from django.core.mail import send_mail
    pending = request.session.get('pending_reserva')
    if not pending:
        return redirect('clientes:panel')

    from clientes.models import Cliente
    cliente = Cliente.objects.filter(user=request.user).first()
    if not cliente:
        return redirect('clientes:registro')

    from reserva.models import Reserva, HorarioDisponible
    from empleados.models import Empleado
    from servicio.models import Servicio

    existe = Reserva.objects.filter(
        cliente=cliente,
        gestora_id=pending['gestora_id'],
        servicio_id=pending['servicio_id'],
        hora_id=pending['hora_id'],
        fecha=pending['fecha']
    ).exists()

    if not existe:
        reserva_obj = Reserva.objects.create(
            cliente=cliente,
            gestora=Empleado.objects.get(id=pending['gestora_id']),
            servicio=Servicio.objects.get(id=pending['servicio_id']),
            hora=HorarioDisponible.objects.get(id=pending['hora_id']),
            fecha=pending['fecha'],
            estado='pendiente'
        )
        # Enviar correo de confirmación al usuario
        correo_destino = cliente.correo or pending.get('correo')
        if correo_destino:
            servicio_nombre = reserva_obj.servicio.nombre
            from datetime import datetime
            if isinstance(reserva_obj.fecha, str):
                fecha_dt = datetime.fromisoformat(reserva_obj.fecha)
            else:
                fecha_dt = reserva_obj.fecha
            fecha = fecha_dt.strftime('%d/%m/%Y')
            hora = reserva_obj.hora.hora.strftime('%H:%M')
            mensaje =  f"Hola {cliente.nombre},\n\nTu cita para '{servicio_nombre}' ha sido agendada para el día {fecha} a las {hora}.\n\n¡Gracias por reservar con Gise-Nails!"
            mensaje_html = f"""
            <div style="font-family: Arial, sans-serif; background: #f9f9f9; padding: 30px;">
                <h2 style="color: #d63384;">¡Cita agendada en Gise-Nails!</h2>
                <p>Hola <b>{cliente.nombre}</b>,</p>
                <p>Tu cita para <b>{servicio_nombre}</b> ha sido agendada para el día <b>{fecha}</b> a las <b>{hora}</b>.</p>
                <p style="margin-top: 40px; color: #555;">¡Gracias por reservar con <b>Gise-Nails</b>!</p>
                <p style="margin-top: 40px;">⚠️ Tu cita debe confirmarse con al menos 1 hora de anticipación. De no hacerlo, será cancelada automáticamente. ¡Gracias por tu puntualidad! </p>
                <h2 style="color: #d63384;">¡Recuerda confirmar tu cita 💖!</h2>
               </div>
            """
            send_mail(
                subject="Confirmación de tu cita en Gise-Nails",
                message=mensaje,
                from_email=None,
                recipient_list=[correo_destino],
                fail_silently=False,
                html_message=mensaje_html
            )
        # --- ENVÍO DE CORREO AL EMPLEADO ---
        gestora = reserva_obj.gestora
        servicio = reserva_obj.servicio
        from datetime import datetime
        if isinstance(reserva_obj.fecha, str):
            fecha_dt = datetime.fromisoformat(reserva_obj.fecha)
        else:
            fecha_dt = reserva_obj.fecha
        fecha = fecha_dt.strftime('%d/%m/%Y')
        hora = reserva_obj.hora.hora.strftime('%H:%M')
        mensaje_empleado = (
            f"¡Nueva cita reservada!\n\n"
            f"Cliente: {cliente.nombre}\n"
            f"Teléfono: {cliente.telefono}\n"
            f"Correo: {cliente.correo}\n"
            f"Servicio: {servicio.nombre}\n"
            f"Fecha: {fecha}\n"
            f"Hora: {hora}\n"
        )
        mensaje_html_empleado = f"""
        <div style="font-family: 'Montserrat', Arial, sans-serif; background: #fff0fa; padding: 32px; border-radius: 18px; box-shadow: 0 2px 18px #ffb6e6;">
            <h2 style="color: #d63384; margin-bottom: 12px;">¡Nueva cita agendada!</h2>
            <p style="font-size: 1.15rem; color: #222;">
                <b>Cliente:</b> {cliente.nombre}<br>
                <b>Teléfono:</b> {cliente.telefono}<br>
                <b>Correo:</b> {cliente.correo}<br>
                <b>Servicio:</b> {servicio.nombre}<br>
                <b>Fecha:</b> <span style="color:#d63384;">{fecha}</span><br>
                <b>Hora:</b> <span style="color:#d63384;">{hora}</span>
            </p>
            <hr style="margin: 24px 0; border: none; border-top: 2px solid #ffb6e6;">
         
            <p style="margin-top: 32px; color: #d63384; font-weight: bold; font-size: 1.2rem;">
                ¡Gracias por tu dedicación! 💅
            </p>
        </div>
        """
        send_mail(
            subject="Nueva cita reservada en Gise-Nails",
            message=mensaje_empleado,
            from_email=None,
            recipient_list=[gestora.correo],
            fail_silently=False,
            html_message=mensaje_html_empleado
        )
    # Limpia la sesión
    if 'pending_reserva' in request.session:
        del request.session['pending_reserva']

    return redirect('clientes:panel')

from django.contrib.auth.models import User

def confirmar_reserva(request, pk):
    # Obtener la reserva pendiente
    reserva = get_object_or_404(Reserva, pk=pk)

    # Verificar si el correo del cliente existe en la base de datos
    cliente_email = reserva.cliente.correo
    if not User.objects.filter(username=cliente_email).exists():
        # Redirigir al login.html con el formulario de registro activo
        return render(request, 'login/login.html', {
            'register_active': True,
            'prefill_email': cliente_email,
            'pending_message': True
        })

    # Lógica para confirmar la reserva si el usuario existe
    reserva.estado = 'confirmada'
    reserva.save()
    messages.success(request, 'La reserva ha sido confirmada exitosamente.')
    return redirect('clientes:panel')

def crear_reserva(request):
    # ... código para procesar el formulario ...
    if request.method == 'POST':
        # Procesa y guarda la reserva
        # reserva = Reserva.objects.create(...)
        # Suponiendo que tienes la instancia reserva creada:
        gestora = reserva.gestora
        servicio = reserva.servicio
        cliente = reserva.cliente
        fecha = reserva.fecha
        hora = reserva.hora

        # Construye el mensaje
        mensaje = (
            f"¡Nueva cita reservada!\n\n"
            f"Cliente: {cliente}\n"
            f"Servicio: {servicio}\n"
            f"Fecha: {fecha}\n"
            f"Hora: {hora}\n"
            f"Teléfono: {cliente.telefono if hasattr(cliente, 'telefono') else ''}\n"
            f"Correo: {cliente.correo if hasattr(cliente, 'correo') else ''}\n"
        )

        send_mail(
            subject="Nueva cita reservada",
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[gestora.correo],  # Asegúrate que gestora tiene correo
            fail_silently=False,
        )
        # ... continúa con la respuesta ...

@login_required
def abonar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk, cliente__user=request.user)
    precio_servicio = reserva.servicio.precio if reserva.servicio else Decimal('0')
    monto_abono = precio_servicio * Decimal('0.3')
    monto_abono = int(monto_abono.to_integral_value(rounding='ROUND_HALF_UP'))
    monto_abono_str = localize(monto_abono)  # Esto pone el punto de miles según configuración regional

    nequi_num = '3153923380'
    daviplata_num = '3153923380'
    if request.method == 'POST':
        form = ReferenciaPagoForm(request.POST)
        if form.is_valid():
            metodo = form.cleaned_data['metodo']
            referencia = form.cleaned_data['referencia']
            PagoReserva.objects.create(
                reserva=reserva,
                cliente=reserva.cliente,
                monto=monto_abono,
                metodo=metodo,
                comprobante=None,
                confirmado=False,
                fecha_pago=timezone.now(),
                referencia=referencia  # Guarda la referencia
            )
            messages.success(request, "Referencia enviada. El equipo validará tu pago y confirmará tu cita.")
            return redirect('clientes:panel')
    else:
        form = ReferenciaPagoForm()
    return render(request, 'reserva/abonar_reserva.html', {
        'reserva': reserva,
        'form': form,
        'monto_abono': monto_abono_str,
        'nequi_num': nequi_num,
        'daviplata_num': daviplata_num,
    })
