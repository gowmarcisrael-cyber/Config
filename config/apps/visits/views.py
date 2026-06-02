from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Visit
from apps.listings.models import Listing
from .forms import VisitForm

# Create your views here.
@login_required
def request_visit(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    
    if listing.user == request.user:
        return redirect('listing_detail', id=pk)
    
    if request.method == 'POST':
        form = VisitForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.listing = listing
            visit.sender = request.user
            visit.receiver = listing.user
            visit.save()
            return redirect('listing_detail', id=pk)
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
    return render(request, 'visits/partials/visit_status.html', {'visit': visit})

@login_required
@require_POST
def cancel_visit(request, pk):
    visit = get_object_or_404(Visit, pk=pk)
    
    # Vérifier que c'est bien l'envoyeur ou le receveur
    if request.user != visit.sender and request.user != visit.receiver:
        return HttpResponse(status=403)
    
    # Ne peut pas annuler une visite déjà annulée ou refusée
    if visit.status in ('Annulée', 'Refusée'):
        return HttpResponse(status=400)
    
    visit.status = 'Annulée'
    visit.save()
    
    return render(request, 'visits/partials/visit_status.html', {'visit': visit})