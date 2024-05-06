from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgencyViewSet, TourViewSet, CityViewSet, CountryViewSet, ReviewViewSet, AddressViewSet

router = DefaultRouter()
router.register(r'agencies', AgencyViewSet)
router.register(r'tours', TourViewSet)
router.register(r'cities', CityViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'addresses', AddressViewSet)

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('accounts/', include('django.contrib.auth.urls')),
]