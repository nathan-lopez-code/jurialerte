from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from alerts.models import Alerte
from dossiers.models import Dossier
from users.forms import LoginForm
from users.models import Utilisateur


@login_required(login_url='users:login')
def index(request):

    dossier_recent = Dossier.objects.all()[:5]
    alerte_imminente = Alerte.objects.filter(
        est_envoyee=False,  # L'alerte ne doit pas avoir déjà été envoyée
        ).order_by('date_declenchement_cible').first()

    dossiers_sans_alerte = Dossier.objects.filter(alertes__isnull=True)

    context = {
        'dossier_recent': dossier_recent,
        'alerte_imminente': alerte_imminente,
        'dossiers_sans_alerte': dossiers_sans_alerte,

    }

    return  render(request, 'base.html', context)


@login_required(login_url='users:login')
def logout_(request):
    logout(request)
    return redirect('users:login')


def login_(request):

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            try:
                utilisateur = Utilisateur.objects.filter(username=username, password=password)[0]
            except:
                utilisateur = None

            if utilisateur is not None:
                login(request, utilisateur)
                return redirect('users:index')
            else:
                context = {
                    'form': form,
                    'error_message' : "mot de passe  ou username incorrect"
                }
                return render(request, 'login.html', context)

    return render(request, 'login.html', {'form': form})