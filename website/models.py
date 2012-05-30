# -*- coding: utf-8 -*-

from django.db import models
from django.forms import ModelForm
from django.conf import settings
from django.db.models.signals import post_save
from django.core.mail import send_mail
import image


# para guardar opciones del sitio (aka switches)
class Setting(models.Model):
    value = models.BooleanField(default=False)
    key = models.CharField(max_length=50)

    def __unicode__(self):
        return self.key


# el archivo de videos
class Video(models.Model):
    titulo = models.CharField(max_length=150)
    slug = models.CharField(max_length=300)
    imagen = models.ImageField(upload_to='videos')
    fecha = models.DateField()
    embed_code = models.TextField()
    descripcion = models.TextField()
    participantes = models.TextField(blank=True)
    activado = models.BooleanField(default=False)

    def __unicode__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        super(Video, self).save(*args, **kwargs)

        if not self.id and not self.imagen:
            return

        image.resize(image.THUMB, self.imagen)
        image.resize(image.SINGLE, self.imagen)
        image.resize(image.HOME, self.imagen)

    # el permalink
    def get_absolute_url(self):
        return '/videos/%s/' % self.slug

    # los diferentes imagenes para el sitio
    def get_home_image_url(self):
        return image.get_url_by(image.HOME, self.imagen)

    def get_thumb_image_url(self):
        return image.get_url_by(image.THUMB, self.imagen)

    def get_single_image_url(self):
        return image.get_url_by(image.SINGLE, self.imagen)


# comentarios de los videos
class VideoComentario(models.Model):
    autor_email = models.EmailField()
    autor_url = models.URLField(blank=True)
    autor = models.CharField(max_length=150)
    fecha = models.DateField(auto_now_add=True)
    content = models.TextField()
    video = models.ForeignKey(Video)

    def __unicode__(self):
        return '%s dijo: %s' % (self.autor, self.content[:100])


# el formulario para agregar un comentario al video
class VideoComentarioForm(ModelForm):
	class Meta:
		model  = VideoComentario
		fields = ('autor', 'autor_email', 'autor_url', 'content')

# el archivo de cursos
class Curso(models.Model):
    titulo 		  = models.CharField(max_length=150)
    slug	      = models.CharField(max_length=300)
    imagen 	      = models.ImageField(upload_to='cursos')
    pais          = models.CharField(max_length=150)
    fecha 	      = models.DateField()
    descripcion   = models.TextField()
    activado      = models.BooleanField(default=False)

    def __unicode__(self):
        return self.titulo

    def get_image_url(self):
        return '%s%s' % (settings.MEDIA_URL, str(self.imagen))


class RegistroCurso(models.Model):
    nombre    = models.CharField(max_length=500)
    email     = models.EmailField()
    telefono  = models.CharField(max_length=300)
    pago      = models.BooleanField(default=False)
    curso     = models.TextField()
    pais      = models.CharField(max_length=100)
    code      = models.CharField(max_length=100)
    personas  = models.IntegerField(default=1)
    total     = models.FloatField()
    descuento = models.FloatField()
    tipo      = models.CharField(max_length=100, default="paypal")
    fecha     = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return '%s en %s' % (self.nombre, self.curso)


# hooks
def registro_post_save(sender, instance, created, *args, **kwargs):
    if created:
        send_mail('Registro al "%s"' % instance.curso, 'Nombre: %s\nEmail: %s\nTelefono: %s\nTipo de pago: %s\nCurso: %s\nPais: %s\n' % (instance.nombre, instance.email, instance.telefono, instance.tipo, instance.curso, instance.pais), settings.FROM_CURSOS_EMAIL, settings.TO_CURSOS_EMAIL)
    if instance.pago:
        send_mail('Pago de "%s"' % instance.curso, '%s (%s) ha realizado el pago de %s por %s persona(s) mediante paypal al "%s"' % (instance.nombre, instance.email, instance.total, instance.personas, instance.curso), settings.FROM_CURSOS_EMAIL, settings.TO_CURSOS_EMAIL)
        

post_save.connect(registro_post_save, sender=RegistroCurso)