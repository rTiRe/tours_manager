"""Module with site urls."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views

from . import views

router = DefaultRouter()
router.register('agencies', views.AgencyViewSet)
router.register('tours', views.TourViewSet)
router.register('reviews', views.ReviewViewSet)
router.register('addresses', views.AddressViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('tours/', views.tours, name='tours'),
    path('agencies/', views.agencies, name='agencies'),
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('registration/', views.registration, name='manager-registration'),
    path('login/', views.login, name='manager-login'),
    path('logout/', views.logout, name='manager-logout'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('password_reset/', views.CustomPasswordResetView.as_view(), {'letter':'let'}, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_complete'),
    path('password_change/', views.request_password_change, name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('confirm_password_change/<uidb64>/<token>/', views.confirm_password_change, name='confirm_password_change'),
    path('password_change/complete/', views.PasswordChangeCompleteView.as_view(), name='password_change_complete'),
]
