from django.urls import path
from . import views

app_name = 'planets'

urlpatterns = [
    path('', views.planets, name='planets'),
]