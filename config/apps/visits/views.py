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
from .tasks import send_visit_status_email,send_visit_request_email
from django.conf import settings
from django.core.cache import cache
# Create your views here.

@login_required
def request_visit(request, slug):
    cache.delete(f'dashboard_{request.user.pk}')
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
            listing_url = request.build_absolute_uri(f"/detail/{visit.listing.slug}/")
            send_visit_request_email.delay(visit.id,listing_url)
            return redirect('listing_detail', slug=slug)
    else:
        form = VisitForm()
    
    return render(request, 'visits/request.html', {
        'form': form,
        'listing': listing,
    })


@login_required
def visits_sent(request):
    cache.delete(f'dashboard_{request.user.pk}')
    visits = Visit.objects.filter(
        sender=request.user).select_related(
            'listing',
            'receiver').prefetch_related('listing__images').only(
            'id',
            'date', 
            'status',
            'message',
            'listing_id',
            'receiver_id',)
    context = {'visits': visits}
    if request.headers.get('HX-Request'):
        return render(request, 'visits/sent_fragment.html', context)
    return render(request, 'visits/sent.html', context=context)


@login_required
def visits_received(request):
    cache.delete(f'dashboard_{request.user.pk}')
    visits = Visit.objects.filter(
        receiver=request.user).select_related(
            'listing',
            'sender').prefetch_related('listing__images').only(
            'id',
            'date', 
            'status',
            'message',
            'listing_id',
            'sender_id',)
    context = {'visits': visits}
    if request.headers.get('HX-request'):
        return render(request, 'visits/received_fragment.html',context=context)
    return render(request, 'visits/received.html', context=context)

@login_required
@require_POST
def update_visit_status(request, pk):
    cache.delete(f'dashboard_{request.user.pk}')
    visit = get_object_or_404(Visit.objects.select_related('listing','sender'),
                              pk=pk, 
                              receiver=request.user)
    new_status = request.POST.get('status')
    if new_status in dict(Visit.STATUS):
        visit.status = new_status
        visit.save(update_fields=['status'])

        # Notifier l'envoyeur
        if new_status == 'Acceptée':
            notify(
                user=visit.sender,
                notif_type='visit_accepted',
                message=f'Votre demande de visite pour "{visit.listing.title}" a été acceptée.',
                link=f'/detail/{visit.listing.slug}/'
            )
        elif new_status == 'Refusée':
            notify(
                user=visit.sender,
                notif_type='visit_refused',
                message=f'Votre demande de visite pour "{visit.listing.title}" a été refusée.',
                link=f'/detail/{visit.listing.slug}/'
            )
        listing_url = request.build_absolute_uri(f"/detail/{visit.listing.slug}/")
        send_visit_status_email.delay(visit.id,listing_url)
    return render(request, 'visits/partials/visit_status.html', {'visit': visit})

@login_required
@require_POST
def cancel_visit(request, pk):
    cache.delete(f'dashboard_{request.user.pk}')
    visit = get_object_or_404(Visit.objects.select_related('listing','sender','receiver'), pk=pk)
    if request.user != visit.sender and request.user != visit.receiver:
        return HttpResponse(status=403)
    if visit.status in ('Annulée', 'Refusée'):
        return HttpResponse(status=400)

    visit.status = 'Annulée'
    visit.save(update_fields=['status'])

    # Notifier l'autre partie
    other_user = visit.receiver if request.user == visit.sender else visit.sender
    notify(
        user=other_user,
        notif_type='visit_cancelled',
        message=f'La visite pour "{visit.listing.title}" a été annulée.',
        link=f'/detail/{visit.listing.slug}/'
    )

    return render(request, 'visits/partials/visit_status.html', {'visit': visit})