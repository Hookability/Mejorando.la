# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.forms.models import model_to_dict
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core import serializers
from django.utils import simplejson
from akismet import Akismet
import GeoIP
import image
from models import Setting, Video, VideoComentario, VideoComentarioForm, Curso, RegistroCurso
import datetime
import time
import requests
import urllib


# La vista del home muestra el ultimo video destacado
# y 4 videos mas, + el horario localizado
def home(solicitud):
    # si no existe el valor aun en la base de datos
    try:
        es_vivo = Setting.objects.get(key='en_vivo').value
    except Setting.DoesNotExist:
        es_vivo = False

    # checar si estamos transmitiendo en vivo
    # regresar la vista de "vivo" de ser asi
    if ('live' in solicitud.GET and solicitud.GET['live'] == '1') or es_vivo:
        return render_to_response('website/live.html')

    # si no hay videos aun
    try:
        ultimo_video = Video.objects.all().filter(activado=True).latest('fecha')
    except Video.DoesNotExist:
        ultimo_video = None

    ultimos_4_videos = Video.objects.all().order_by('-fecha').filter(activado=True)[1:5]
    # plantilla
    return render_to_response('website/home.html', {
        'ultimo_video': ultimo_video,  # El ultimo video
        'videos': ultimos_4_videos,  # ultimos 4 videos
        'pais': get_pais(solicitud.META),  # el horario del programa localizado
        'timestamp': get_timestamp(),  # Obtiene el timestamp del sig. program.
        'cursos': Curso.objects.all().order_by('fecha').filter(activado=True, fecha__gte=datetime.datetime.now())
    })


def siguiente_jueves_4pm(now):
    _4PM = datetime.time(hour=16)
    _JUE = 3  # Monday=0 for weekday()
    old_now = now
    now += datetime.timedelta((_JUE - now.weekday()) % 7)
    now = now.combine(now.date(), _4PM)
    if old_now >= now:
        now += datetime.timedelta(days=7)
    return now


def get_timestamp():
    now = datetime.datetime.now()
    sig_jueves = siguiente_jueves_4pm(now)
    return int(time.mktime(sig_jueves.timetuple()) * 1000)

# el archivo de cursos 
# organizados por mes-año
def cursos(solicitud):
	return render_to_response('website/cursos.html', {
		'meses': [{
			'fecha' : fecha,
			'cursos': Curso.objects.filter(fecha__year=fecha.year, fecha__month=fecha.month, activado=True).order_by('-fecha')
		} for fecha in Curso.objects.filter(activado=True).dates('fecha', 'month', order='DESC')]
	})

# el archivo muestra todos los videos
# organizados por mes-año
def videos(solicitud):
    return render_to_response('website/videos.html', {
        'meses': [{
            'fecha': fecha,
            'videos': Video.objects.filter(fecha__year=fecha.year,
                                        fecha__month=fecha.month, activado=True).order_by('-fecha')
        } for fecha in Video.objects.filter(activado=True).dates('fecha', 'month', order='DESC')]
    })


# la entrada de video muestra el video
# del capitulo + comentarios + formulario de comentarios
# tambien procesa +1 comentario
def video(solicitud, video_slug):
    # video por slug (nombre)
    video = get_object_or_404(Video, slug=video_slug)

    # si son datos del formulario de comentarios
    if solicitud.method == 'POST':
        form = VideoComentarioForm(solicitud.POST)

        # validar los datos
        if(form.is_valid()):
            # asignar el video
            comentario = form.save(commit=False)
            comentario.video = video

            # detectar spam
            api = Akismet(key=settings.AKISMET_API_KEY,
                        blog_url=settings.AKISMET_URL,
                        agent=settings.AKISMET_AGENT)
            if api.verify_key():
                # por si el usuario esta detras de un proxy
                if 'HTTP_X_FORWARDED_FOR' in solicitud.META and solicitud.META['HTTP_X_FORWARDED_FOR']:
                    ip = solicitud.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
                else:
                    ip = solicitud.META['REMOTE_ADDR']

                if not api.comment_check(comment=comentario.content, data={
                        'user_ip': ip,
                        'user_agent': solicitud.META['HTTP_USER_AGENT']
                    }):

                    # guardar el video
                    comentario.save()
    else:
        form = VideoComentarioForm()

    comentarios = VideoComentario.objects.filter(video_id=video.id).\
                                            order_by('-fecha', '-id')
    return render_to_response('website/video.html', {
        'video': video,  # datos del video particular
        'form': form,  # formulario de comentarios
        'comentarios': comentarios  # comentarios al video
    })


# plantilla de transmision en vivo
def live(solicitud):
    return render_to_response('website/live.html')


# volver a generar las imagenes de video
# en todos sus sizes
@login_required()
def regenerate(solicitud):
    for video in Video.objects.all():
        image.resize(image.THUMB, video.imagen)
        image.resize(image.SINGLE, video.imagen)
        image.resize(image.HOME, video.imagen)

    for curso in Curso.objects.all():
        image.resize(image.THUMB, curso.imagen)

    return redirect('/')


def handler404(solicitud):
    return redirect('website.views.home')


# devuelve el horario del programa
# localizado por pais gracias a la
# libreria GeoIP
def get_pais(meta):
    geo = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)

    # por si el usuario esta detras de un proxy
    if 'HTTP_X_FORWARDED_FOR' in meta and meta['HTTP_X_FORWARDED_FOR']:
        ip = meta['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        ip = meta['REMOTE_ADDR']

    country = geo.country_name_by_addr(ip)
    if country is None:
        country = ''

    return country


from django.http import HttpResponse

@require_POST
def cursos_registro(solicitud):

    if solicitud.POST.get('nombre') and solicitud.POST.get('telefono') and solicitud.POST.get('email') and solicitud.POST.get('curso') and solicitud.POST.get('code') and solicitud.POST.get('total'):
        if RegistroCurso.objects.filter(email=solicitud.POST.get('email'), code=solicitud.POST.get('code')).exists():
            return HttpResponse('ERROR: Ya te has registrado a este curso.')

        registro = RegistroCurso(nombre=solicitud.POST.get('nombre'), telefono=solicitud.POST.get('telefono'), email=solicitud.POST.get('email'), curso=solicitud.POST.get('curso'), pais=get_pais(solicitud.META), code=solicitud.POST.get('code'), total=solicitud.POST.get('total'))

        if solicitud.POST.get('personas'):
            registro.personas = int(solicitud.POST.get('personas'))

        if solicitud.POST.get('descuento'):
            registro.descuento = float(solicitud.POST.get('descuento'))

        if solicitud.POST.get('tipo'):
            registro.tipo = solicitud.POST.get('tipo')

        registro.save()

        solicitud.session['registro_id'] = registro.id

        return HttpResponse('OK')

    return HttpResponse('ERROR')

def cursos_pago_success(solicitud):

    if solicitud.POST.get('payer_email') and solicitud.POST.get('transaction_subject'):
        registro = RegistroCurso.objects.get(email=solicitud.POST.get('payer_email'), curso=solicitud.POST.get('transaction_subject'))

        if not registro and solicitud.session.get('registro_id'):
            registro = RegistroCurso.get(id=solicitud.session.get('registro_id'))

        if registro:
            registro.pago = True
            registro.save()
    elif solicitud.session.get('registro_id'):
        registro = RegistroCurso.get(id=solicitud.session.get('registro_id'))        

        if registro:
            registro.pago = True
            registro.save()

    return redirect('/cursos')

@login_required(login_url='/admin')
def cursos_registros(solicitud):
    return render_to_response('website/cursos_registros.html', { 'registros': serializers.serialize('json', RegistroCurso.objects.all()) })


def locateme(solicitud):
    return HttpResponse(get_pais(solicitud.META))


def hola(solicitud):

    if solicitud.method == 'POST' and solicitud.POST.get('email') and solicitud.POST.get('nombre'):
        pais   = get_pais(solicitud.META)
        email  = solicitud.POST['email']
        nombre = solicitud.POST['nombre']

        # por si el usuario esta detras de un proxy
        if solicitud.META.get('HTTP_X_FORWARDED_FOR'):
            ip = solicitud.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
        else:
            ip = solicitud.META['REMOTE_ADDR']

        payload = {
            'email_address': email,
            'apikey': settings.MAILCHIMP_APIKEY,
            'merge_vars': {
                'FNAME': nombre,
                'OPTINIP': ip,
                'OPTIN_TIME': time.time()
            },
            'id': settings.MAILCHIMP_LISTID,
            'email_type': 'html'
        }

        r = requests.post('http://us2.api.mailchimp.com/1.3/?method=listSubscribe', simplejson.dumps(payload))

        return HttpResponse(r.text)

    return render_to_response('website/hola.html', {})

@login_required(login_url='/admin')
def usuarios_chat(solicitud):
    from pymongo import Connection

    conn = Connection()

    db = conn[settings.CHAT_DB]
    users = []
    for u in db.users.find():
        if u['name'] is None: continue

        users.append({
            'name': u['name'],
            'red': u['red'],
            'messages': db.messages.find({ 'user.name' : u['name'] }).count(),
        })

    return render_to_response('website/usuarios_chat.html', { 'usuarios': simplejson.dumps(users) })