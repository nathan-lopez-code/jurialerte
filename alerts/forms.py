from django import forms
from .models import Alerte  # Importez le modèle Alerte mis à jour
from django.utils import timezone
from users.models import Utilisateur  # Assurez-vous d'importer votre modèle Utilisateur


class AlerteForm(forms.ModelForm):

    date_evenement_initial = forms.DateTimeField(
        label="Date de l'événement (si applicable)",
        required=False,  # La validation spécifique sera gérée dans clean()
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        help_text="Ex: Date de l'audience. Requis pour le type 'Audience Fixée' multiple."
    )

    message = forms.CharField(
        label="Message de l'alerte",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        help_text="Un message personnalisé pour cette alerte. Si vide, un message par défaut sera généré."
    )

    delai_jours = forms.IntegerField(
        label="Délai en jours",
        required=False,  # Peut être rempli par défaut ou déduit
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Décalage en jours par rapport à la date de l'événement (négatif pour avant)."
    )

    delai_heures = forms.IntegerField(
        label="Délai en heures",
        required=False,  # Peut être rempli par défaut ou déduit
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Décalage en heures par rapport à la date de l'événement (négatif pour avant)."
    )

    est_multiple = forms.BooleanField(
        label="Génère plusieurs notifications",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        # Utilisation de form-check-input pour Bootstrap 4/5
        help_text="Cochez si ce type d'alerte génère plusieurs notifications (ex: 48h et 12h avant l'événement)."
    )

    destinataires = forms.ModelMultipleChoiceField(
        queryset=Utilisateur.objects.all().order_by('username'),  # Peupler avec tous les utilisateurs
        label="Destinataires de l'alerte",
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Sélectionnez les utilisateurs qui recevront cette alerte."
    )

    class Meta:
        model = Alerte
        # Incluez tous les champs que vous voulez permettre à l'utilisateur de modifier ou de sélectionner
        fields = [
            'nom_type', 'description_type', 'est_multiple',
            'delai_jours', 'delai_heures', 'date_evenement_initial',
            'message', 'destinataires'
        ]
        widgets = {
            'nom_type': forms.Select(attrs={'class': 'form-control'}),
            'description_type': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            # 'date_evenement_initial' et 'message' déjà définis avec widgets
            # 'est_multiple', 'delai_jours', 'delai_heures' ont déjà des widgets implicites/explicites
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Appliquer la classe 'form-control' à tous les champs textuels et de sélection
        for field_name, field in self.fields.items():
            if isinstance(field.widget,
                          (forms.TextInput, forms.Select, forms.Textarea, forms.DateTimeInput, forms.NumberInput)):
                field.widget.attrs.update({'class': 'form-control'})
            # Pour les checkboxes, utilisez 'form-check-input' et entourez-les d'un 'form-check' div dans le template
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            # Pour ModelMultipleChoiceField avec CheckboxSelectMultiple, chaque option doit être stylisée dans le template.
            # Ici, nous ne pouvons pas directement ajouter des classes aux <li> ou aux <label> qu'il génère.
            # Cela devra être géré dans le template HTML.

    def clean(self):
        cleaned_data = super().clean()
        nom_type = cleaned_data.get('nom_type')
        est_multiple = cleaned_data.get('est_multiple')  # Maintenant directement depuis le formulaire
        date_evenement_initial = cleaned_data.get('date_evenement_initial')

        if nom_type == "audience" and est_multiple and not date_evenement_initial:
            self.add_error('date_evenement_initial',
                           "Pour une alerte 'Audience Fixée' de type 'multiple', une date d'événement initiale est obligatoire.")

        # S'assurer que date_evenement_initial est 'timezone-aware' si fournie
        if date_evenement_initial and timezone.is_naive(date_evenement_initial):
            cleaned_data['date_evenement_initial'] = timezone.make_aware(date_evenement_initial)


        return cleaned_data