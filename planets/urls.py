from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'planets'

router = DefaultRouter()

router.register(r'planets', views.PlanetViewSet, basename='planet')
router.register(r'starsystems', views.StarSystemViewSet, basename='starsystem')
router.register(r'stars', views.StarViewSet, basename='star')

urlpatterns = [
    path('', views.planets, name='planets'),
    path('api/', include(router.urls)),
]