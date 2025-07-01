from datetime import datetime, timezone, timedelta
from sqlite3 import IntegrityError

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # Si vous avez besoin d'authentification
from django.views.decorators.http import require_POST
from pyexpat.errors import messages
from django.utils import timezone

from alerts.models import Alerte
from .forms import DossierForm, EvenementCleForm
from .models import Dossier, EtapeDossier


@login_required(login_url='users:login')
def dossier_detail(request, pk):
    dossier = get_object_or_404(Dossier, pk=pk)

    # --- Logique existante de consultation du dossier ---
    last_etape = EtapeDossier.objects.filter(
        auteur=request.user,
        dossier=dossier,
    ).order_by('-date_mise_a_jour').first()

    current_time = timezone.now()
    add_consultation_etape = False

    if last_etape:
        if (current_time - last_etape.date_mise_a_jour) > timezone.timedelta(hours=24):
            add_consultation_etape = True
    else:
        add_consultation_etape = True

    if add_consultation_etape:
        nom_user = request.user.first_name + " " + request.user.last_name
        date_str = current_time.strftime('%d/%m/%Y %H:%M')
        EtapeDossier.objects.create(
            dossier=dossier,
            type_etape='consultation',
            action_menee=f"Dossier consulté par {nom_user} en date du {date_str}.",
            auteur=request.user
        )

    # --- Récupération des étapes pour l'affichage ---
    # Récupérer tous les types d'étapes importants existants pour ce dossier
    types_specifiques_evenements_cles = [
        'audience', 'depot_conclusion', 'jugement_rendu', 'reouverture'
    ]

    # Récupérer les types d'étapes existants pour ce dossier parmi les "types_specifiques_evenements_cles"
    existing_important_etape_types = EtapeDossier.objects.filter(
        dossier=dossier,
        type_etape__in=types_specifiques_evenements_cles
    ).values_list('type_etape', flat=True).distinct()

    # Convertir le QuerySet en liste pour faciliter la manipulation dans le gabarit ou le formulaire
    existing_important_etape_types_list = list(existing_important_etape_types)


    initial_evenement_choices = []
    for value, display_name in EvenementCleForm.TYPES_EVENEMENTS_CLES:
        if value not in existing_important_etape_types_list:
            initial_evenement_choices.append((value, display_name))

    # Si toutes les options sont déjà prises, nous pouvons ajouter une option par défaut vide
    if not initial_evenement_choices and len(types_specifiques_evenements_cles) > 0:

        messages.info(request, "Toutes les étapes clés (Audience, Dépôt, Jugement, Réouverture) ont déjà été enregistrées pour ce dossier.")

    evenement_form = EvenementCleForm()
    evenement_form.fields['type_evenement'].choices = initial_evenement_choices
    if not initial_evenement_choices:
        evenement_form.fields['type_evenement'].required = False
        evenement_form.fields['type_evenement'].choices = [('', 'Toutes les options sont utilisées')]


    etapes_important = EtapeDossier.objects.filter(dossier=dossier, type_etape__in=types_specifiques_evenements_cles).distinct()
    etapeDossier = EtapeDossier.objects.filter(dossier=dossier).order_by('-date_mise_a_jour')

    if request.method == 'POST':
        if 'submit_evenement_form' in request.POST:
            # Re-créer le formulaire avec les choix filtrés pour la validation POST
            evenement_form = EvenementCleForm(request.POST)
            evenement_form.fields['type_evenement'].choices = initial_evenement_choices # Appliquer les mêmes filtres

            if evenement_form.is_valid():
                type_evenement = evenement_form.cleaned_data['type_evenement']


                EtapeDossier.objects.create(
                    dossier=dossier,
                    type_etape=type_evenement,
                    action_menee=f"Événement clé '{type_evenement}' enregistré le {timezone.now().strftime('%d/%m/%Y %H:%M')}.",
                    auteur=request.user
                )
                return redirect('dossiers:detail_dossier', pk=dossier.pk)

            return redirect('dossiers:detail_dossier', pk=dossier.pk)

    context = {
        'dossier': dossier,
        'etapeDossier': etapeDossier,
        'etapes_important': etapes_important,
        'evenement_form': evenement_form,
        'dossier_alert' : Alerte.objects.filter(dossier=dossier).first(),
    }

    return render(request, 'detail_dossier.html', context)



@login_required
def creer_dossier(request):
    if request.method == 'POST':
        form = DossierForm(request.POST)
        if form.is_valid():
            dossier = form.save()
            if dossier.auteur is None:
                dossier.auteur = request.user
                dossier.save()

            EtapeDossier.objects.create(
                dossier=dossier,
                auteur = request.user,
                action_menee = 'creation du dossier juridique',
                type_etape = 'creation'
            ).save()

            return redirect('dossiers:detail_dossier', pk=dossier.pk) # Assurez-vous d'avoir cette URL
    else:
        form = DossierForm()
    return render(request, 'creat_dossier.html', {'form': form})



@login_required
def modifier_dossier(request, pk):
    """
    Vue pour modifier un dossier existant.
    Elle récupère un dossier par sa clé primaire (pk),
    préremplit le formulaire avec ses données, et gère la soumission du formulaire.
    """
    dossier = get_object_or_404(Dossier, pk=pk)


    if request.method == 'POST':

        form = DossierForm(request.POST, instance=dossier)
        if form.is_valid():
            form.save()
            EtapeDossier.objects.create(
                dossier=dossier,
                auteur=request.user,
                action_menee=f'Modification du dossier juridique valeur changer {
                    form.data
                }',
                type_etape='modification'
            ).save()
            return redirect('dossiers:detail_dossier', pk=dossier.pk)
    else:
        form = DossierForm(instance=dossier)

    return render(request, 'modifier_dossier.html', {'form': form, 'dossier': dossier})


@login_required
def gestion_dossier(request):

    all_dossiers = Dossier.objects.all()

    return render(request, 'gestion_dossier.html', {'all_dossiers': all_dossiers})