from django.db import models
from django.urls import reverse
import datetime
from django.utils import timezone
from django.db import transaction # Import transaction for better error handling

from dossiers.models import Dossier
from users.models import Utilisateur


class Alerte(models.Model):
    # ... (your existing model fields are fine) ...
    TYPE_ALERTE_CHOICES = [
        ('audience', 'Audience Fixée'),
        ('conclusion', 'Dépôt de Conclusion'),
        ('jugement', 'Jugement à Rendre'),
        # Ajoutez d'autres types ici
    ]

    nom_type = models.CharField(max_length=100, choices=TYPE_ALERTE_CHOICES,
                                help_text="Le type d'alerte prédéfini.")
    description_type = models.TextField(blank=True, null=True,
                                        help_text="Description détaillée du type d'alerte.")
    est_multiple = models.BooleanField(default=False,
                                       help_text="Cochez si cette alerte génère plusieurs notifications (ex: 48h et 12h avant l'événement).")
    delai_jours = models.IntegerField(default=0,
                                      help_text="Nombre de jours de décalage par rapport à la date de l'événement initial (négatif si avant, positif si après).")
    delai_heures = models.IntegerField(default=0,
                                       help_text="Nombre d'heures de décalage par rapport à la date de l'événement initial (négatif si avant, positif si après).")

    # Champs spécifiques à l'instance d'Alerte
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name='alertes',
                                help_text="Le dossier auquel cette alerte est liée.")
    date_evenement_initial = models.DateTimeField(null=True, blank=True,
                                                  help_text="Date de l'événement principal (ex: date d'audience), utilisé pour calculer les déclenchements.")
    date_declenchement_cible = models.DateTimeField(
        help_text="Date et heure exactes à laquelle cette alerte spécifique doit être envoyée.")
    date_creation = models.DateTimeField(auto_now_add=True,
                                         help_text="Date et heure de création de l'alerte.")
    message = models.TextField(blank=True, null=True,
                               help_text="Message spécifique pour cette instance d'alerte. Si vide, un message par défaut sera généré.")
    est_envoyee = models.BooleanField(default=False,
                                      help_text="Indique si la notification SMS a été envoyée pour cette alerte.")
    date_envoi = models.DateTimeField(blank=True, null=True,
                                      help_text="Date et heure de l'envoi effectif de la notification SMS.")
    destinataires = models.ManyToManyField(Utilisateur, related_name='alertes_recues',
                                           help_text="Utilisateurs spécifiques qui recevront cette alerte.")
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='alertes_creees',
                                 help_text="L'utilisateur qui a créé cette alerte.")

    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
        ordering = ['date_declenchement_cible']

    def __str__(self):
        return (f"Alerte [{self.get_nom_type_display()}] pour dossier {self.dossier.numero_dossier} "
                f"à envoyer le {self.date_declenchement_cible.strftime('%Y-%m-%d %H:%M') if self.date_declenchement_cible else 'N/A'}")

    def get_absolute_url(self):
        return reverse('alerts:alerte_detail', kwargs={'pk': self.pk})


    def save(self, *args, **kwargs):
        _prevent_recursion = kwargs.pop('_prevent_recursion', False)

        # 1. Handle timezone and date_declenchement_cible calculation BEFORE saving the main object
        #    This ensures the main object is properly prepared before it hits the DB.
        if not self.date_declenchement_cible:
            if self.date_evenement_initial:
                self.date_declenchement_cible = self.date_evenement_initial + \
                                                datetime.timedelta(days=self.delai_jours,
                                                                   hours=self.delai_heures)
            else:
                self.date_declenchement_cible = timezone.now() + \
                                                datetime.timedelta(days=self.delai_jours,
                                                                   hours=self.delai_heures)

        if self.date_declenchement_cible and timezone.is_naive(self.date_declenchement_cible):
            self.date_declenchement_cible = timezone.make_aware(self.date_declenchement_cible,
                                                                timezone.get_current_timezone())

        # 2. Call super().save() FIRST to ensure the main object gets an ID.
        #    This is critical for the M2M relationships to work for the initial object.
        #    We only call super().save() if it's the primary save, not the recursive ones.
        if not _prevent_recursion:  # Only save the primary instance if it's not a recursive call
            super().save(*args, **kwargs)
        else:
            # If it's a recursive call, we still need to save this specific instance
            # but we use super().save() to avoid re-triggering the parent logic.
            super().save(*args, **kwargs)

        # 3. Handle the multiple alert creation AFTER the main object (self) has been saved
        #    and has an ID. This logic only runs IF this is the initial creation.
        if self._state.adding and not _prevent_recursion:
            if self.nom_type == "audience" and self.est_multiple:
                if not self.date_evenement_initial:
                    raise ValueError(
                        "Pour une alerte 'Audience Fixée' de type 'multiple', 'date_evenement_initial' est obligatoire.")

                with transaction.atomic():
                    # --- Création de l'alerte 48h avant l'événement initial ---
                    alerte_48h = Alerte(
                        dossier=self.dossier,
                        nom_type=self.nom_type,  # Keep the same type for generated alerts
                        description_type="Rappel 48h avant audience",  # Specific description for this sub-alert
                        est_multiple=False,  # These sub-alerts are not multiple themselves
                        delai_jours=0,
                        delai_heures=0,
                        date_evenement_initial=self.date_evenement_initial,
                        date_declenchement_cible=self.date_evenement_initial - datetime.timedelta(hours=48),
                        message="Rappel: Votre audience aura lieu dans 48 heures.",  # Specific message
                        cree_par=self.cree_par,
                    )
                    alerte_48h.save(_prevent_recursion=True)  # Now `alerte_48h` gets its ID
                    alerte_48h.destinataires.set(self.destinataires.all())
                    print(f"Création de l'alerte 'Audience Fixée - 48h' pour dossier {self.dossier.numero_dossier}")

                    # --- Création de l'alerte 12h avant l'événement initial ---
                    alerte_12h = Alerte(
                        dossier=self.dossier,
                        nom_type=self.nom_type,  # Keep the same type for generated alerts
                        description_type="Rappel 12h avant audience",  # Specific description for this sub-alert
                        est_multiple=False,  # These sub-alerts are not multiple themselves
                        delai_jours=0,
                        delai_heures=0,
                        date_evenement_initial=self.date_evenement_initial,
                        date_declenchement_cible=self.date_evenement_initial - datetime.timedelta(hours=12),
                        message="Rappel: Votre audience aura lieu dans 12 heures.",  # Specific message
                        cree_par=self.cree_par,
                    )
                    alerte_12h.save(_prevent_recursion=True)  # Now `alerte_12h` gets its ID
                    alerte_12h.destinataires.set(self.destinataires.all())
                    print(f"Création de l'alerte 'Audience Fixée - 12h' pour dossier {self.dossier.numero_dossier}")
                return

        if not self.date_declenchement_cible:
            if self.date_evenement_initial:
                self.date_declenchement_cible = self.date_evenement_initial + \
                                                datetime.timedelta(days=self.delai_jours,
                                                                   hours=self.delai_heures)
            else: # Fallback if no initial event date, use current time
                self.date_declenchement_cible = timezone.now() + \
                                                datetime.timedelta(days=self.delai_jours,
                                                                   hours=self.delai_heures)

        # Assurer que la date_declenchement_cible est timezone-aware
        if self.date_declenchement_cible and timezone.is_naive(self.date_declenchement_cible):
            self.date_declenchement_cible = timezone.make_aware(self.date_declenchement_cible,
                                                                timezone.get_current_timezone())

        # C'est la sauvegarde de l'instance "parent" ou d'une alerte simple (non multiple, non 'audience')
        super().save(*args, **kwargs)