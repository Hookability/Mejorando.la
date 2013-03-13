# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from os.path import join

register = template.Library()


@register.simple_tag
def static2(path):
    return join(settings.STATIC2_URL, path)
