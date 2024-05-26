from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email.',
    'zientenin@mail.ru',
    ['wolordkit@gmail.com'],
    fail_silently=False,
)