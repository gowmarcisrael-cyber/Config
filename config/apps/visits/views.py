from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Visit
from apps.listings.models import Listing
from .forms import VisitForm
from django.contrib import messages
from apps.notifications.views import notify

# Create your views here.
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