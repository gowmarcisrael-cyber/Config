from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Visit
from apps.listings.models import Listing
from .forms import VisitForm
from django.contrib import messages
from apps.notifications.views import notify
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# Create your views here.
def send_visit_request_email(request, visit):
    subject = f"Nouvelle demande de visite — {visit.listing.title}"
    html_content = render_to_string(
        "emails/visit_request.html",
        {
            "sender": visit.sender.username,
            "listing": visit.listing,
            "date": visit.date,
            "message": visit.message,
            "listing_url": request.build_absolute_uri(f"/detail/{visit.listing.slug}/"),
        }
    )
    text_content = f"Nouvelle demande de visite de {visit.sender.username} pour {visit.listing.title}"

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [visit.receiver.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

def send_visit_status_email(request, visit):
    subject = f"Demande de visite {visit.status} — {visit.listing.title}"
    html_content = render_to_string(
        "emails/visit_status_update.html",
        {
            "sender": visit.sender.username,
            "receiver": visit.receiver.username,
            "listing": visit.listing,
            "date": visit.date,
            "message": visit.message,
            "status": visit.status,
            "listing_url": request.build_absolute_uri(f"/listings/{visit.listing.slug}/"),
        }
    )
    text_content = f"Votre demande de visite pour {visit.listing.title} a été {visit.status}."

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [visit.sender.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


@login_required
def request_visit(request, slug):
    listing = get_object_or_404(Listing.objects.select_related('user'), slug=slug)
    
    if listing.user == request.user:
        return redirect('listing_detail', slug=slug)
    
    if request.method == 'POST':
        form = VisitForm(request.POST)
        if form.is_valid():
            already_requested = Visit.objects.filter(
                listing=listing,
                sender=request.user,
                status='En attente' # Ajuste selon tes statuts réels
            ).exists()
            if already_requested:
                error_msg = "Vous avez déjà une demande de visite en attente pour ce bien."
                messages.error(request,error_msg)
                return render(request,'visits/error.html')
            visit = form.save(commit=False)
            visit.listing = listing
            visit.sender = request.user
            visit.receiver = listing.user
            visit.save()
            send_visit_request_email(request,visit)
            return redirect('listing_detail', slug=slug)
    else:
        form = VisitForm()
    
    return render(request, 'visits/request.html', {
        'form': form,
        'listing': listing,
    })


@login_required
def visits_sent(request):
    visits = Visit.objects.filter(sender=request.user).select_related('listing', 'receiver')
    return render(request, 'visits/sent.html', {'visits': visits})


@login_required
def visits_received(request):
    visits = Visit.objects.filter(receiver=request.user).select_related('listing', 'sender')
    return render(request, 'visits/received.html', {'visits': visits})

@login_required
@require_POST
def update_visit_status(request, pk):
    visit = get_object_or_404(Visit, pk=pk, receiver=request.user)
    new_status = request.POST.get('status')
    if new_status in dict(Visit.STATUS):
        visit.status = new_status
        visit.save()

        # Notifier l'envoyeur
        if new_status == 'Acceptée':
            notify(
                user=visit.sender,
                type='visit_accepted',
                message=f'Votre demande de visite pour "{visit.listing.title}" a été acceptée.',
                link=f'/detail/{visit.listing.slug}/'
            )
        elif new_status == 'Refusée':
            notify(
                user=visit.sender,
                type='visit_refused',
                message=f'Votre demande de visite pour "{visit.listing.title}" a été refusée.',
                link=f'/detail/{visit.listing.slug}/'
            )
        send_visit_status_email(request,visit)
    return render(request, 'visits/partials/visit_status.html', {'visit': visit})

@login_required
@require_POST
def cancel_visit(request, pk):
    visit = get_object_or_404(Visit, pk=pk)
    if request.user != visit.sender and request.user != visit.receiver:
        return HttpResponse(status=403)
    if visit.status in ('Annulée', 'Refusée'):
        return HttpResponse(status=400)

    visit.status = 'Annulée'
    visit.save()

    # Notifier l'autre partie
    other_user = visit.receiver if request.user == visit.sender else visit.sender
    notify(
        user=other_user,
        type='visit_cancelled',
        message=f'La visite pour "{visit.listing.title}" a été annulée.',
        link=f'/detail/{visit.listing.slug}/'
    )

    return render(request, 'visits/partials/visit_status.html', {'visit': visit})

from django.core.mail import EmailMultiAlternatives

def test_email(request):

    subject = "Bienvenue sur notre plateforme 🏠"

    text_content = "Bienvenue sur notre site immobilier"

    html_content = """
    <h1>Bienvenue 👋</h1>
    <p>Ton compte a été créé avec succès.</p>
    <a href="https://example.com" style="
        padding:10px 15px;
        background:#3b82f6;
        color:white;
        text-decoration:none;
        border-radius:5px;
    ">
        Activer mon compte
    </a>
    """

    email = EmailMultiAlternatives(
        subject,
        text_content,
        "gowmarcisrael@gmail.com",
        ["gowmarcisrael9@gmail.com"]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

    return HttpResponse("Email HTML envoyé !")