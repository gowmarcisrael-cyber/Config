from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    STATUS_CREATE = [
        ('En vente', 'En vente'),
        ('A louer', 'A louer'),
    ]

    status = forms.ChoiceField(choices=STATUS_CREATE)

    class Meta:
        model = Listing
        exclude = ['user', 'is_available', 'created_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }