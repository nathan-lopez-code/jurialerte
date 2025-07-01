from django import forms
from .models import Dossier, EtapeDossier
from users.models import Utilisateur # Assurez-vous d'importer Utilisateur si ce n'est pas déjà fait

class DossierForm(forms.ModelForm):
    """
    Formulaire basé sur le modèle Dossier pour créer ou modifier un dossier.
    """
    class Meta:
        model = Dossier
        # Spécifiez les champs que vous voulez inclure dans le formulaire
        # Vous pouvez lister tous les champs du modèle ou utiliser '__all__'
        fields = [
            'numero_dossier',
            'nom_affaire',
            'description',
            'statut',
            'magistrat_responsable',
            'greffier_responsable',
            'contact_partie',
            'numero_telephone_partie',
        ]
        # Alternativement, vous pouvez utiliser fields = '__all__' pour inclure tous les champs,
        # ou exclude = ['date_creation'] pour exclure des champs spécifiques (comme date_creation
        # qui est auto_now_add=True).

        # Vous pouvez également ajouter des widgets personnalisés ou des labels ici
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}), # Pour une zone de texte plus grande
        }
        labels = {
            'numero_dossier': "Numéro du Dossier",
            'nom_affaire': "Nom de l'Affaire",
            'description': "Description du Dossier",
            'statut': "Statut",
            'magistrat_responsable': "Magistrat Responsable",
            'greffier_responsable': "Greffier Responsable",
            'contact_partie': "Contact de la Partie",
            'numero_telephone_partie': "Numéro de Téléphone de la Partie",
        }
        help_texts = {
            # Vous pouvez aussi surcharger le help_text du modèle ici si besoin
            # 'numero_dossier': "Entrez un numéro unique pour le dossier.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des QuerySets pour les ForeignKeys
        # Limite les choix pour 'magistrat_responsable' aux utilisateurs ayant le rôle 'magistrat'
        self.fields['magistrat_responsable'].queryset = Utilisateur.objects.filter(role='magistrat')
        # Limite les choix pour 'greffier_responsable' aux utilisateurs ayant le rôle 'greffier'
        self.fields['greffier_responsable'].queryset = Utilisateur.objects.filter(role='greffier')

        # Ajoutez des classes CSS à tous les champs pour le stylisme (ex: Bootstrap)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.EmailInput, forms.NumberInput)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'


class EvenementCleForm(forms.Form):
    """
    Formulaire non basé sur un modèle pour enregistrer des événements clés spécifiques.
    """

    # Utiliser les choices du modèle EtapeDossier pour les types spécifiques
    # C'est une bonne pratique pour éviter la duplication de logique.
    TYPES_EVENEMENTS_CLES = [
        choice for choice in EtapeDossier.TYPE_ETAPE_CHOICES
        if choice[0] in ['audience', 'depot_conclusion', 'jugement_rendu', 'reouverture']
    ]

    type_evenement = forms.ChoiceField(
        choices=TYPES_EVENEMENTS_CLES,
        label="Sélectionnez l'événement clé",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Textarea, forms.Select, forms.DateTimeInput)):
                current_class = field.widget.attrs.get('class', '')
                if 'form-control' not in current_class:
                    field.widget.attrs['class'] = (current_class + ' form-control').strip()