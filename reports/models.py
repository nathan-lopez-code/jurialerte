from django.db import models
from django.conf import settings # Pour lier à l'utilisateur qui génère le rapport
from django.urls import reverse

from dossiers.models import Dossier # Assurez-vous d'avoir importé votre modèle Dossier

class Report(models.Model):
    """
    Modèle représentant un rapport généré à la demande.
    """
    # Nom descriptif du rapport, peut être généré automatiquement
    name = models.CharField(max_length=255, verbose_name="Nom du rapport")
    # Période couverte par le rapport
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    # Date et heure de la génération du rapport
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="Généré le")
    # Utilisateur qui a généré le rapport
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_reports',
        verbose_name="Généré par"
    )
    # Champ pour stocker le fichier PDF du rapport
    pdf_file = models.FileField(
        upload_to='media/reports/pdfs/',
        blank=True,
        null=True,
        verbose_name="Fichier PDF"
    )

    class Meta:
        verbose_name = "Rapport"
        verbose_name_plural = "Rapports"
        ordering = ['-generated_at'] # Trie par le plus récent en premier

    def __str__(self):
        return f"Rapport '{self.name}' du {self.start_date} au {self.end_date}"

    def get_absolute_url(self):

        return reverse('reports:report_detail', args=[str(self.id)])
