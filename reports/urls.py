from django.urls import path
from .views import list_rapport, generate_report_view, download_report

app_name = 'reports'
urlpatterns = [
    path('list/', list_rapport, name='list_rapport'),
    path('generer/', generate_report_view, name='generate_report'),
    path('<int:report_id>/telechargement', download_report, name='download_report'),
]