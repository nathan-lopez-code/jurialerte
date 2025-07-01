from django.db import models
from users.models import Utilisateur


class Dossier(models.Model):

    STATUS_DOSSIER = (
        ('Ouvert', 'Ouvert'),
        ('Clos', 'Clos'),
        ('En attente', 'En attente'),
    )

    numero_dossier = models.CharField(max_length=50, unique=True, help_text="Numéro unique du dossier")
    nom_affaire = models.CharField(max_length=255, help_text="Nom de l'affaire ou du litige")
    date_creation = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=50, choices=STATUS_DOSSIER, default='ouvert', help_text="Statut actuel du dossier (ouvert, clos, en attente...)")
    magistrat_responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='dossiers_magistrat', limit_choices_to={'role': 'magistrat'}, help_text="Magistrat en charge du dossier")
    greffier_responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='dossiers_greffier', limit_choices_to={'role': 'greffier'}, help_text="Greffier assigné au dossier")
    contact_partie = models.CharField(max_length=255, blank=True, null=True, help_text="Contact principal ou partie impliquée")
    numero_telephone_partie = models.CharField(max_length=20, blank=True, null=True, help_text="Numéro de téléphone de la partie pour certaines notifications")

    auteur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    class Meta:
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"
        # Tri par date de création, du plus récent au plus ancien
        ordering = ['-date_creation']

    def __str__(self):
        return f"Dossier n°{self.numero_dossier} - {self.nom_affaire}"


class EtapeDossier(models.Model):
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name='etapes')
    date_mise_a_jour = models.DateTimeField(auto_now_add=True, help_text="Date et heure de la mise à jour")
    auteur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, help_text="Utilisateur ayant effectué l'action (auteur)")
    action_menee = models.TextField(help_text="Description détaillée de l'action menée ou de l'étape")
    TYPE_ETAPE_CHOICES = (
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('consultation', 'Consultation'),
        ('audience', 'Audience'),
        ('depot_conclusion', 'Dépôt de conclusion'),
        ('jugement_rendu', 'Jugement rendu'),
        ('reouverture', 'Réouverture'),
        ('autre', 'Autre'),
    )

    type_etape = models.CharField(max_length=50, choices=TYPE_ETAPE_CHOICES, default='autre', help_text="Catégorie de l'action")

    class Meta:
        verbose_name = "Étape du Dossier"
        verbose_name_plural = "Historique des Étapes des Dossiers"
        # Tri chronologique des étapes
        ordering = ['date_mise_a_jour']

    def __str__(self):
        return f"[{self.dossier.numero_dossier}] {self.type_etape} par {self.auteur} le {self.date_mise_a_jour.strftime('%Y-%m-%d %H:%M')}"