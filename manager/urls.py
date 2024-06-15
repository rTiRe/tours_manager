"""Module with site urls."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import (authentication_views, password_change_views, profile_views,
               views, viewset_views)

router = DefaultRouter()
router.register('agencies', viewset_views.AgencyViewSet)
router.register('tours', viewset_views.TourViewSet)
router.register('reviews', viewset_views.ReviewViewSet)
router.register('addresses', viewset_views.AddressViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('tours/', views.tours, name='tours'),
    path('agencies/', views.agencies, name='agencies'),
    path('profile/', profile_views.my_profile, name='my_profile'),
    path('profile/<str:username>/', profile_views.profile, name='profile'),
    path('settings/', profile_views.settings, name='settings'),
    path('registration/', authentication_views.registration, name='manager-registration'),
    path('login/', authentication_views.login, name='manager-login'),
    path('logout/', authentication_views.logout, name='manager-logout'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('password_reset/', password_change_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', password_change_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', password_change_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/complete/', password_change_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password_change/', password_change_views.request_password_change, name='password_change'),
    path('password_change/done/', password_change_views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('change/<uidb64>/<token>/', password_change_views.confirm_password_change, name='confirm_password_change'),
    path('change/complete/', password_change_views.CustomPasswordResetCompleteView.as_view(), name='password_change_complete'),
    path('tour/<uuid:uuid>/', views.tour, name='tour'),
    path('tour/<uuid:uuid>/edit/', views.edit_tour, name='edit_tour'),
    path('tour/<uuid:uuid>/delete/', views.delete_tour, name='delete_tour'),
    path('tour/create/', views.create_tour, name='create_tour'),
]
