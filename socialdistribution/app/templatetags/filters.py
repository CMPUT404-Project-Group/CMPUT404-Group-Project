from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import SafeString
import markdown

register = template.Library()

@register.filter
@stringfilter
def commonmark(value):
    return markdown.Markdown().convert(value)
