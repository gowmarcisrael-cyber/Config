from django import forms
from django.core.exceptions import ValidationError
from .models import Listing
import bleach

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

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise ValidationError("Le prix doit être supérieur à 0.")
        return price

    def clean_bedrooms(self):
        bedrooms = self.cleaned_data['bedrooms']
        if bedrooms < 0:
            raise ValidationError("Le nombre de chambres ne peut pas être négatif.")
        return bedrooms

    def clean_bathrooms(self):
        bathrooms = self.cleaned_data['bathrooms']
        if bathrooms < 0:
            raise ValidationError("Le nombre de salles de bain ne peut pas être négatif.")
        return bathrooms

    def clean_latitude(self):
        latitude = self.cleaned_data['latitude']
        if latitude < -90 or latitude > 90:
            raise ValidationError("La latitude doit être entre -90 et 90.")
        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data['longitude']
        if longitude < -180 or longitude > 180:
            raise ValidationError("La longitude doit être entre -180 et 180.")
        return longitude
    
    def clean_area(self):
        area = self.cleaned_data['area']
        if area <= 0:
            raise ValidationError('entrer la "surface correcte')
        return area
        
    def clean_title(self):
        title = self.cleaned_data['title']
        return bleach.clean(title, tags=[], strip=True)

    def clean_description(self):
        description = self.cleaned_data['description']
        return bleach.clean(description, tags=[], strip=True) 