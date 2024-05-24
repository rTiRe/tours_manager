from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def pop_item(dictionary, key):
    return dictionary.pop(key)

@register.filter
def make_str(item):
    return str(item)

@register.filter
def to_int(value):
    return int(value)