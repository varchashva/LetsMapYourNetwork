from django import template

register = template.Library()

from celery.result import AsyncResult

@register.filter(name='split')
def split(value):
    try:
        return value.split("#")[1].split('@')[0]
    except Exception as ex:
        return str(ex)

@register.filter(name='parsehistory')
def parsehistory(value):
    try:
        return str(value.split("@")[0]) + " " + str(value.split("@")[2] + AsyncResult(value.split("@")[1]).state)
    except Exception as ex:
        return str(ex)