"""Module with site urls."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('agencies', views.AgencyViewSet)
router.register('tours', views.TourViewSet)
router.register('reviews', views.ReviewViewSet)
router.register('addresses', views.AddressViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('tours/', views.tours, name='tours'),
    path('tours', views.tours, name='tours'),
    path('agencies/', views.agencies, name='agencies'),
    path('agencies', views.agencies, name='agencies'),
    path('profile/', views.profile, name='my_profile'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('accounts/', include('django.contrib.auth.urls')),
]
