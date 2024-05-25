from django import template
from django.utils.safestring import SafeText, mark_safe

register = template.Library()

@register.filter(is_safe=True)
def get_errors_html(errors: dict, expected_field_name: str) -> SafeText:
    if errors and expected_field_name in errors.keys():
        li_template = '<li><i class="fa-solid fa-triangle-exclamation"></i> {error}</li>'
        field_errors = []
        for field_name in errors.keys():
            if field_name == expected_field_name:
                field_errors.append(li_template.format(error=errors[field_name]))
        if field_errors:
            field_errors_as_string = ''.join(field_errors)
            return mark_safe(f'<span class="errors"><ul>{field_errors_as_string}</ul></span>')
    return mark_safe('')

