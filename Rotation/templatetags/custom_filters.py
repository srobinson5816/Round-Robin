from django import template
from django.template.defaultfilters import date
from django.utils.timezone import localtime

register = template.Library()

@register.filter(expects_localtime=True)
def custom_date(value, format_string="F d, Y H:i"):
    return date(localtime(value), format_string)
