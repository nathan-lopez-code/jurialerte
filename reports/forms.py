from django import forms

class ReportGenerationForm(forms.Form):
    start_date = forms.DateField(
        label="Date de début",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        label="Date de fin",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("La date de début ne peut pas être postérieure à la date de fin.")
        return cleaned_data