from django import forms
from .models import Visit

class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['date', 'message']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }