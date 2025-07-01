from django.conf.urls.static import static
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
import os

# Importez vos modèles
from dossiers.models import Dossier  # Assurez-vous que Dossier a une relation 'etapes' ou un champ 'date_creation'
from .models import Report
from .forms import ReportGenerationForm

# Pour la génération PDF (assurez-vous que WeasyPrint est installé et configuré)
from weasyprint import HTML, CSS
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage


@login_required(login_url='users:login')
def list_rapport(request):

    rapport = Report.objects.all().order_by('-generated_at')

    context = {'reports': rapport}

    return render(request, 'list_rapport.html', context)


@login_required
def generate_report_view(request):
    """
    Vue pour générer un rapport sur une période donnée.
    Permet d'afficher le rapport et de le télécharger en PDF.
    """
    report = None
    form = ReportGenerationForm()

    if request.method == 'POST':
        form = ReportGenerationForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            dossiers_period = Dossier.objects.filter(
                date_creation__gte=start_date,
                date_creation__lte=end_date,
            ).distinct().order_by('date_creation')
            relative_logo_url = staticfiles_storage.url('images/logos/logo_.png')
            logo_url_for_weasyprint = request.build_absolute_uri(relative_logo_url)

            print(f"Debug : {logo_url_for_weasyprint}")

            report_html = render_to_string('report_detail.html', {
                'start_date': start_date,
                'end_date': end_date,
                'dossiers': dossiers_period,
                'generated_at': timezone.now(),
                'generated_by': request.user.get_full_name() or request.user.username,
                'logo_url': logo_url_for_weasyprint,
            })

            # --- Génération du PDF ---
            # Crée un objet Report dans la base de données
            report_name = f"Rapport_Dossiers_{start_date}_{end_date}_{request.user.first_name}"
            new_report = Report(
                name=report_name,
                start_date=start_date,
                end_date=end_date,
                generated_by=request.user,
            )
            # Sauvegarder d'abord pour avoir un ID si nécessaire pour le chemin du fichier
            new_report.save()

            # Chemin où le PDF sera sauvegardé (dans le dossier MEDIA_ROOT)
            pdf_filename = f"{report_name}_{new_report.id}.pdf"
            pdf_path = os.path.join(settings.MEDIA_ROOT, 'reports', 'pdfs', pdf_filename)
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)  # Assure que le dossier existe

            HTML(string=report_html).write_pdf(pdf_path)

            # Mettre à jour l'objet Report avec le chemin du fichier PDF
            new_report.pdf_file.name = os.path.join('reports', 'pdfs', pdf_filename)
            new_report.save()  # Sauvegarde à nouveau pour mettre à jour le champ pdf_file

            report = new_report  # Pour afficher le lien de téléchargement après la génération
            messages.success(request, "Rapport généré et sauvegardé avec succès.")

        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")

    context = {
        'form': form,
        'report': report,  # Passera le rapport généré pour l'affichage/téléchargement
    }
    return render(request, 'generate_report.html', context)


@login_required(login_url='users:login')
def download_report(request, report_id):
    """
    Vue pour télécharger un rapport PDF existant.
    """
    report = get_object_or_404(Report, id=report_id)

    if not report.pdf_file:
        messages.error(request, "Le fichier PDF pour ce rapport n'a pas été trouvé.")
        return redirect('reports:list_reports')  # Redirige vers la liste des rapports

    # Ouvre le fichier en mode binaire
    try:
        with open(report.pdf_file.path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{report.name}.pdf"'
            return response
    except FileNotFoundError:
        messages.error(request, "Le fichier PDF n'existe plus sur le serveur.")
        report.pdf_file.delete(save=True)  # Supprime la référence si le fichier n'est plus là
        return redirect('reports:list_rapport')