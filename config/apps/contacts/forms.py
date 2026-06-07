from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200, required=False)
    message = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        fields = ['name','email','subject','message']
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if not name:
            raise ValidationError('Veuillez entrer un nom')
        return name
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError('Veuillez entrer une adresse email')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Veuillez entrer une adresse email valide')
        return email
    
    def clean_message(self):
        message = self.cleaned_data['message']
        if not message:
            raise ValidationError('Veuillez entrer un message')
        return message