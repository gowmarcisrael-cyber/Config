from django.shortcuts import render,redirect
from .models import Message
import bleach
from django.contrib import messages
from .forms import ContactForm

# Create your views here.
def contact(request):
    if request.method == 'POST':
        # Honeypot - si rempli c'est un bot
        if request.POST.get('q'):
            messages.success(request, 'Votre message a bien été envoyé.')
            return redirect('contact')
        message = ContactForm(request.POST)
        if message.is_valid():
            name = bleach.clean(message.cleaned_data['name'],strip=True,tags=[],attributes={})
            email = bleach.clean(message.cleaned_data['email'],strip=True,tags=[],attributes={})
            subject = bleach.clean(message.cleaned_data['subject'],strip=True,tags=[],attributes={})
            message = bleach.clean(message.cleaned_data['message'],strip=True,tags=[],attributes={})
            Message.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )
            message.success(request,'Votre message a bien été envoyé.')
            return redirect('contact')
        else:
            print('erreur',message.errors)
    else:
        message = ContactForm()
    return render(request, 'page/contact.html',context={
        'form':ContactForm
    })