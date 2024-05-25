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

@register.filter
def get_avg(int_list):
    if isinstance(int_list, dict):
        int_list = [dict_value for dict_value in int_list.values()]
    int_list = list(filter(lambda number: number != 0, int_list))
    if int_list:
        return sum(int_list) / len(int_list)
    return 0