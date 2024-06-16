"""Utils for work with user profile."""

from django.views.generic.base import View

from .errors_utils import convert_errors


def create_stylized_auth_view(style_files: list | tuple) -> View:
    """Add styles for views.

    Args:
        style_files: list | tuple - pathes of css files.

    Returns:
        View: stylized view.
    """
    def class_decorator(original_class: object) -> View:
        class CustomView(original_class):
            def get_context_data(self, **kwargs):
                errors = {}
                context = super().get_context_data(**kwargs)
                form = context.get('form')
                if form:
                    errors = form.errors.as_data()
                    errors = convert_errors(errors)
                context['errors'] = errors
                context['style_files'] = style_files
                return context
        return CustomView
    return class_decorator
