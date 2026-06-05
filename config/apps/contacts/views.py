from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from .models import Message
import bleach
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages

# Create your views here.
def contact(request):
    if request.method == 'POST':
        # Honeypot - si rempli c'est un bot
        if request.POST.get('q'):
            messages.success(request, 'Votre message a bien été envoyé.')
            return redirect('contact')

        name = bleach.clean(request.POST.get('name', ''), tags=[], strip=True)
        email = bleach.clean(request.POST.get('email', ''), tags=[], strip=True)
        subject = bleach.clean(request.POST.get('subject', ''), tags=[], strip=True)
        message = bleach.clean(request.POST.get('message', ''), tags=[], strip=True)

        if not name or not email or not message:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return redirect('contact')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Adresse email invalide.')
            return redirect('contact')

        Message.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )
        messages.success(request, 'Votre message a bien été envoyé.')
    return render(request, 'page/contact.html')