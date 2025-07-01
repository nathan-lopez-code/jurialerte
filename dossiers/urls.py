from django.urls import path
from .views import creer_dossier, modifier_dossier, gestion_dossier, dossier_detail


app_name = 'dossiers'


urlpatterns = [
    path('creation/', creer_dossier, name="creer_dossier"),
    path('list/', gestion_dossier, name="gestion_dossier"),
    path('<int:pk>/dossier/', dossier_detail, name="detail_dossier"),
    path('<int:pk>/modifer/', modifier_dossier, name="modifier_dossier"),
]