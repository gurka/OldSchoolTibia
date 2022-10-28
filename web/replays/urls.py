from django.urls import path

from . import views

urlpatterns = [
    path('', views.versions, name='versions'),
    path('<str:version>/', views.version, name='version'),
]
