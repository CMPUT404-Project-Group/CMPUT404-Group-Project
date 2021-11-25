from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import SafeString
import markdown

register = template.Library()

@register.filter
@stringfilter
def commonmark(value):
    return markdown.Markdown().convert(value)

@register.filter(name="getID")
def get_ID(value):
    return value.split('/')[-1]

@register.filter(name="getNav")
def get_nav(value):
    return value.split('/')[-2]