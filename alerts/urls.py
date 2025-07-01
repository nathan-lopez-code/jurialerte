from django.urls import path
from .views import creer_alerte, liste_alertes

app_name = 'alerts'

urlpatterns = [
    path('creation/pour/<int:dossier_id>/', creer_alerte, name='creation_alerte'),
    path('programme/', liste_alertes, name='liste_alertes'),
]