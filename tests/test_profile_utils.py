from django import forms
from django.test import RequestFactory, TestCase
from django.views.generic import TemplateView

from manager.views_utils.profile_utils import create_stylized_auth_view

STYLE = 'style.css'


class StylizedAuthViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_stylized_view_without_errors(self):
        @create_stylized_auth_view([STYLE])
        class TestView(TemplateView):
            template_name = 'test.html'
        request = self.factory.get('/')
        response = TestView.as_view()(request)
        self.assertEqual(response.context_data['style_files'], [STYLE])

    def test_stylized_view_with_errors(self):
        @create_stylized_auth_view([STYLE])
        class TestView(TemplateView):
            template_name = 'test.html'

            def get_context_data(subself, **kwargs):
                context = super().get_context_data(**kwargs)
                context['form'] = self.get_form({'field': ''})
                return context

            def get_form(subself, form_data):

                class TestForm(forms.Form):
                    field = forms.CharField(required=True)
                return TestForm(data=form_data)
        request = self.factory.get('/')
        response = TestView.as_view()(request)
        self.assertIn('errors', response.context_data)
        self.assertTrue(isinstance(response.context_data['errors'], dict))
        self.assertIn('style_files', response.context_data)
        self.assertEqual(response.context_data['style_files'], [STYLE])
