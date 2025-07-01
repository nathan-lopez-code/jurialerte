from django.urls import path
from .views import index, login_, logout_

app_name = 'users'


urlpatterns = [
    path('', index, name='index'),
    path('login/', login_, name='login'),
    path('logout/', logout_, name='logout'),
]