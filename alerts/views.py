import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from dossiers.models import Dossier
from .forms import AlerteForm
from .models import Alerte


@login_required(login_url='users:login')
def liste_alertes(request):

    alerts_no_send = Alerte.objects.filter(est_envoyee=False)
    alerts_send = Alerte.objects.filter(est_envoyee=True)

    context = {
        'alerts_no_send': alerts_no_send,
        'alerts_send': alerts_send,
    }

    return render(request, 'gestion _alerte.html', context)


@login_required(login_url='users:login')
def creer_alerte(request, dossier_id):
    """
    Vue pour créer une nouvelle alerte liée à un dossier spécifique.

    Args:
        request: L'objet HttpRequest.
        dossier_id: L'ID du dossier auquel l'alerte sera liée.

    Returns:
        HttpResponse: Rend le template de création d'alerte ou redirige.
    """
    dossier = get_object_or_404(Dossier, pk=dossier_id)

    type_properties = {
        'audience': {
            'description_type': "Alerte pour fixer une audience.",
            'est_multiple': True,
            'delai_jours': 0,
            'delai_heures': 0
        },
        'conclusion': {
            'description_type': "Alerte pour dépôt de conclusions.",
            'est_multiple': False,
            'delai_jours': 7,
            'delai_heures': 0
        },
        'jugement': {
            'description_type': "Alerte pour un jugement à rendre.",
            'est_multiple': True,
            'delai_jours': 0,
            'delai_heures': 0
        },
    }

    if request.method == 'POST':

        form = AlerteForm(request.POST)
        if form.is_valid():
            alerte = form.save(commit=False)
            alerte.dossier = dossier
            alerte.cree_par = request.user

            selected_type_key = alerte.nom_type
            if selected_type_key in type_properties:
                props = type_properties[selected_type_key]
                alerte.description_type = props['description_type']
                alerte.est_multiple = props['est_multiple']
                alerte.delai_jours = props['delai_jours']
                alerte.delai_heures = props['delai_heures']
            else:
                # Gère le cas où un type d'alerte inattendu est soumis (devrait être empêché par le formulaire côté client).
                messages.error(request, "Type d'alerte sélectionné non reconnu.")
                return render(request, 'creer_alerte.html',
                              {'form': form, 'dossier': dossier, 'type_properties_json': json.dumps(type_properties)})

            alerte.save()

            form.save_m2m()

            messages.success(request,
                             f"L'alerte de type '{alerte.get_nom_type_display()}' a été créée avec succès pour le dossier {dossier.numero_dossier}.")
            return redirect('dossiers:detail_dossier', pk=dossier.pk)
        else:
            messages.error(request, "Erreur lors de la création de l'alerte. Veuillez vérifier les champs.")

    else:
        form = AlerteForm()

    context = {
        'form': form,
        'dossier': dossier,
        'type_properties_json': json.dumps(type_properties)  # Passe les propriétés des types d'alerte au template sous forme JSON.
    }
    return render(request, 'creer_alerte.html', context)