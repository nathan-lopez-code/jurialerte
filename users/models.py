from django.db import models
from django.contrib.auth.models import AbstractUser

class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('magistrat', 'Magistrat'),
        ('greffier', 'Greffier'),
        ('secretaire', 'Secrétaire'),
    )
    profile_image = models.ImageField(upload_to='media/profile_images', blank=True, null=True, help_text="Photo de profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    numero_telephone = models.CharField(max_length=20, blank=True, null=True, help_text="Numéro de téléphone pour les notifications SMS")

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        permissions = [
            ("can_view_all_reports", "Peut consulter tous les rapports statistiques"),
            ("can_update_dossier", "Peut mettre a jour le dossier")
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


    def full_name(self):
        return f"{self.first_name} {self.last_name}"