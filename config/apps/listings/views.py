from django.shortcuts import render, redirect,get_object_or_404
from .models import Listing,Favorite
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from .forms import ListingForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from apps.visits.models import Visit
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.reports.models import Report
from django.contrib.postgres.search import SearchQuery,SearchVector,SearchRank
# Create your views here.

def home(request):
    listings = Listing.objects.filter(is_available=True,is_approved=True)[:6]
    context = {
        'listings':listings,
        'types':Listing.TYPES,
        'statuses':Listing.STATUS[:2],
        }
    return render(request,'listings/index.html',context=context)

def search(request):
    listings = Listing.objects.filter(is_available=True,is_approved=True)

    status = request.GET.get('status')
    city = request.GET.get('city')
    property_type = request.GET.get('property_type')
    price_max = request.GET.get('price_max')
    query = request.GET.get('q')

    if status:
        listings = listings.filter(status=status)
    if city:
        listings = listings.filter(city__icontains=city)
    if property_type:
        listings = listings.filter(property_type=property_type)
    if price_max:
        listings = listings.filter(price__lte=price_max)

    if query:
        search_vector = SearchVector('title', weight='A') + SearchVector('description', weight='B') + SearchVector('city', weight='C')
        search_query = SearchQuery(query)
        listings = listings.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(rank__gte=0).order_by('-rank')


    page = request.GET.get('page')
    listings = Paginator(listings, 6).get_page(page)
    
    context = {
        'listings': listings,
        'types': Listing.TYPES,
        'statuses': Listing.STATUS[:2],
        'filters': request.GET,
    }
    return render(request, 'listings/search.html', context=context)

def detail(request,id):
    listing = get_object_or_404(Listing,id=id)
    images = listing.images.all()
    similars = Listing.objects.filter(
        property_type=listing.property_type,
        city=listing.city
    ).exclude(id=listing.id)[:4]
    context = {
        'listing': listing,
        'images': images,
        'similars': similars,
        'report_reasons': Report.REASONS,
    }
    return render(request, 'listings/details.html', context=context)

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        images = request.FILES.getlist('images')
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            for image in images:
                listing.images.create(image=image)
            return redirect('listing_detail', id=listing.id)
    else:
        form = ListingForm()
    return render(request, 'listings/create.html', {'form': form})

# listings/views.py
def get_dashboard_context(user):
    return {
        'listings_count': Listing.objects.filter(user=user).count(),
        'favorites_count': Favorite.objects.filter(user=user).count(),
        'visits_received_count': Visit.objects.filter(receiver=user).count(),
        'visits_sent_count': Visit.objects.filter(sender=user).count(),
        'visits_pending_count': Visit.objects.filter(receiver=user, status='En attente').count(),
    }

@login_required
def dashboard(request):
    listings = Listing.objects.filter(user=request.user).order_by('-created_at')
    context = {
        **get_dashboard_context(request.user),
        'listings': listings,
        'active_tab': 'listings',
    }
    return render(request, 'dashboard/index.html', context)

@login_required
@require_POST
def listing_delete(request,pk):
    listing = get_object_or_404(Listing,pk=pk,user=request.user)
    listing.delete()
    return HttpResponse('')

@login_required
@require_POST
def listing_change_status(request, pk):
    listing = get_object_or_404(Listing, pk=pk, user=request.user)
    new_status = request.POST.get('status')
    if new_status in dict(Listing.STATUS):
        listing.status = new_status
        listing.save()
    return render(request, 'dashboard/partials/status_badge.html', {'listing': listing})

@login_required
@require_http_methods(['GET', 'POST'])
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ListingForm(instance=listing)
    return render(request, 'listings/edit.html', {'form': form, 'listing': listing})

@login_required
@require_POST
def toggle_favorite(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    favorite = Favorite.objects.filter(
        user=request.user,
        listing=listing
    ).first()

    if favorite:
        favorite.delete()
        is_favorite = False
    else:
        Favorite.objects.create(
            user=request.user,
            listing=listing
        )
        is_favorite = True

    return render(
        request,
        "listings/partials/favorite_btn.html",
        {
            "listing": listing,
            "is_favorite": is_favorite,
        }
    )

@login_required
def listings_favorite(request):

    listings = Listing.objects.filter(
        favorites__user=request.user
    ).distinct()
    context = {
        'listings': listings
        }
    return render(request,'dashboard/favorite.html',context=context)

def city_autocomplete(request):
    q = request.GET.get('q', '')
    if len(q) < 2:
        return JsonResponse([], safe=False)
    
    cities = Listing.objects.filter(
        city__icontains=q,
        is_available=True,
        is_approved=True
    ).values_list('city', flat=True).distinct()[:8]
    
    return JsonResponse(list(cities), safe=False)