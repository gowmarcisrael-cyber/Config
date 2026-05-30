from django import forms
from .models import Visit
from django.utils import timezone
from django.core.exceptions import ValidationError

class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['date', 'message']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        if date < timezone.now():
            raise ValidationError('La date ne peut pas être dans le passé.')
        return date