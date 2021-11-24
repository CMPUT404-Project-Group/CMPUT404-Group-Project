from django import template

register = template.Library()

@register.filter(name="getID")
def get_ID(value):
    return value.split('/')[-1]