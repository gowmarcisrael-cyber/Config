import os
from django.shortcuts import render, redirect,get_object_or_404
from .models import Listing,Images
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from .forms import ListingForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from apps.visits.models import Visit
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from apps.reports.models import Report
from django.contrib.postgres.search import SearchQuery,SearchVector,SearchRank
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
import json
from django_ratelimit.decorators import ratelimit
# Create your views here.

def home(request):
    listings = cache.get('home_listings')
    if listings is None:
        listings = Listing.objects.filter(
            is_available=True,
            is_approved=True).exclude(status__in=['Vendu','Loué']).select_related(
                'user'
                ).prefetch_related(
                'images',
                'likes').only(
                'id', 'title', 'price', 'city', 'property_type', 'status', 'slug', 'user__id', 'user__username'
                )[:6]
        listings = list(listings)

        cache.set('home_listings',listings,10*60)

    context = {
        'listings':listings,
        'types':Listing.TYPES,
        'statuses':Listing.STATUS[:2],
        }
    return render(request,'listings/index.html',context=context)

def search(request):
    listings = Listing.objects.filter(
        is_available=True,
        is_approved=True
    ).select_related('user').prefetch_related('likes', 'images').only(
        'id', 'title', 'slug', 'price', 'city', 'property_type', 
        'status', 'bedrooms', 'bathrooms', 'area',
        'latitude', 'longitude', 'user__id', 'user__username'
    )

    status = request.GET.get('status')
    city = request.GET.get('city')
    property_type = request.GET.get('property_type')
    price_max = request.GET.get('price_max')
    query = request.GET.get('q')

    try:
        longitude = float(request.GET.get('longitude') or 0)
        latitude = float(request.GET.get('latitude') or 0)
    except (ValueError, TypeError):
        longitude = 0
        latitude = 0

    if status:
        listings = listings.filter(status=status)
    if city and not longitude and not latitude:
        listings = listings.filter(city__icontains=city)
    if property_type:
        listings = listings.filter(property_type=property_type)
    if price_max:
        try:
            listings = listings.filter(price__lte=int(price_max))
        except ValueError:
            pass

    if longitude and latitude:
        listings = listings.filter(
            longitude__range=(longitude - 0.3, longitude + 0.3),
            latitude__range=(latitude - 0.3, latitude + 0.3),
        )

    if query:
        search_vector = (
            SearchVector('title', weight='A') +
            SearchVector('description', weight='B') +
            SearchVector('city', weight='C')
        )
        search_query = SearchQuery(query)
        listings = listings.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(rank__gt=0).order_by('-rank')
    else:
        listings = listings.order_by('-created_at')

    page = request.GET.get('page')
    listings = Paginator(listings, 6).get_page(page)

    context = {
        'listings': listings,
        'types': Listing.TYPES,
        'statuses': Listing.STATUS[:2],
        'filters': request.GET,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'listings/partials/listings_results.html', context)
    return render(request, 'listings/search.html', context)

@require_POST
def map_recommandation(request):
    try:
        longitude = float(request.POST.get('longitude'))
        latitude = float(request.POST.get('latitude'))
    except (ValueError,TypeError):
        return HttpResponse(status=400)
    delta = 0.1
    listings = Listing.objects.filter(
        is_available=True,
        is_approved=True,
        longitude__range=(longitude - delta, longitude + delta),
        latitude__range=(latitude - delta, latitude + delta),
    ).order_by('-created_at')[:5]

    return render(request, 'listings/map_recommandation.html',context={
        "listing":listings,
    })

def detail(request, slug):
    listing = cache.get(f'listing-{slug}')
    if listing is None:
        listing = get_object_or_404(
            Listing.objects.select_related('user').prefetch_related('likes', 'images'),
            slug=slug
        )
        cache.set(f'listing-{slug}', listing, 2 * 60)

    images = listing.images.all()

    similars = cache.get(f'similars-{slug}')
    if similars is None:
        similars = list(Listing.objects.filter(
            property_type=listing.property_type,
            city=listing.city,
            is_available=True,
            is_approved=True,
        ).exclude(slug=listing.slug).select_related('user').prefetch_related('likes', 'images')[:4])
        cache.set(f'similars-{slug}', similars, 2 * 60)

    context = {
        'listing': listing,
        'images': images,
        'similars': similars,
        'report_reasons': Report.REASONS,
    }
    return render(request, 'listings/details.html', context)

@login_required
@ratelimit(key='user',rate='3/m',method='POST',block=True)
def create_listing(request):
    if request.method == 'POST':
        cache.delete(f'dashboard_{request.user.pk}')
        cache.delete('home_listings')
        cache.delete('map_listings_json')
        form = ListingForm(request.POST)
        images = request.FILES.getlist('images')
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            for image in images:
                listing.images.create(image=image)
            return redirect('listing_detail', slug=listing.slug)
        else :
            print('erreur',form.errors)
    else:
        form = ListingForm()
    return render(request, 'listings/create.html', {'form': form})


def get_dashboard_context(user):
    visit_stats = Visit.objects.aggregate(
        received=Count('id', filter=Q(receiver=user)),
        sent=Count('id', filter=Q(sender=user)),
        pending=Count('id', filter=Q(receiver=user, status='En attente'))
    )
    
    return {
        'listings_count': Listing.objects.filter(user=user).count(),
        'favorites_count': Listing.objects.filter(likes=user).count(),
        
        # On extrait les données calculées en une seule fois
        'visits_received_count': visit_stats['received'],
        'visits_sent_count': visit_stats['sent'],
        'visits_pending_count': visit_stats['pending'],
    }

@login_required
def dashboard(request):
    cache_key = f'dashboard_{request.user.pk}'
    context = cache.get(cache_key)
    
    if context is None:
        listings = Listing.objects.filter(user=request.user).order_by(
            '-created_at'
        ).prefetch_related('images').only(
            'id', 'title', 'price', 'city', 
            'property_type', 'status', 'slug',
        )
        context = {
            **get_dashboard_context(request.user),
            'listings': list(listings),
            'active_tab': 'listings',
        }
        cache.set(cache_key, context, 2 * 60)
    
    return render(request, 'dashboard/index.html', context)

@login_required
@require_POST
def listing_delete(request,slug):
    cache.delete(f'listing-{slug}')
    cache.delete(f'similars-{slug}')
    cache.delete('home_listings')
    cache.delete('map_listings_json')
    cache.delete(f'dashboard_{request.user.pk}')
    listing = get_object_or_404(Listing,slug=slug,user=request.user)
    for img in listing.images.all():
        if img.image and os.path.isfile(img.image.path):
            os.remove(img.image.path)
    listing.delete()
    return HttpResponse('')

@login_required
@require_POST
def listing_change_status(request, slug):
    cache.delete(f'dashboard_{request.user.pk}')
    cache.delete(f'listing-{slug}')
    listing = get_object_or_404(Listing, slug=slug, user=request.user)
    new_status = request.POST.get('status')
    if new_status in dict(Listing.STATUS):
        listing.status = new_status
        if new_status in ['Vendu', 'Loué']: # Ajuste selon tes valeurs réelles
            listing.is_available = False
        else:
            listing.is_available = True
        listing.save(update_fields=['status','is_available','updated_at'])
    return render(request, 'dashboard/partials/status_badge.html', {'listing': listing})

@login_required
@require_http_methods(['GET', 'POST'])
def listing_edit(request, slug):
    cache.delete(f'dashboard_{request.user.pk}')
    cache.delete(f'listing-{slug}')
    cache.delete(f'similars-{slug}')
    listing = get_object_or_404(Listing, slug=slug, user=request.user)
    
    if request.method == 'POST':
        # On passe l'instance existante pour la mettre à jour au lieu de créer un doublon
        form = ListingForm(request.POST, request.FILES, instance=listing)
        images = request.FILES.getlist('images')
        
        # Récupérer les IDs des images que l'utilisateur a coché pour suppression
        images_to_delete = request.POST.getlist('delete_images')
        
        if form.is_valid():
            # Sauvegarde des modifications textuelles (le slug se mettra à jour si le titre change)
            listing = form.save()
            
            # Gestion des suppressions d'images
            if images_to_delete:
                Images.objects.filter(id__in=images_to_delete, listing=listing).delete()
            
            # Gestion des nouvelles images ajoutées
            for image in images:
                listing.images.create(image=image)
                
            messages.success(request, "Votre annonce a été modifiée avec succès.")
            return redirect('listing_detail', slug=listing.slug)
    else:
        # En mode GET, on pré-remplit le formulaire avec l'instance
        form = ListingForm(instance=listing)
        
    return render(request, 'listings/edit.html', {
        'form': form,
        'listing': listing, # On passe l'objet pour afficher ses images actuelles dans le HTML
    })

@login_required
@require_POST
def toggle_favorite(request, slug):
    cache.delete(f'dashboard_{request.user.pk}')
    listing = get_object_or_404(Listing, slug=slug)

    if request.user in listing.likes.all():
        listing.likes.remove(request.user)
        is_favorite = False
    else:
        listing.likes.add(request.user)
        is_favorite = True

    return render(
        request,
        "listings/partials/favorite_btn.html",
        {
            "listing": listing,
            "is_favorite": is_favorite
        }
    )

@login_required
def listings_favorite(request):

    listings = request.user.liked_listings.filter(is_available=True,is_approved=True).prefetch_related('likes','images').order_by('-created_at').only(
        'id',
        'title',
        'city',
        'area',
        'bathrooms',
        'bedrooms',
        'status',
        'property_type',
        'slug'
    )
    context = {
        'listings': listings
        }
    return render(request,'dashboard/favorite.html',context=context)

@cache_page(60 * 2)
def city_autocomplete(request):
    q = request.GET.get('q', '')
    if len(q) < 2:
        return JsonResponse([], safe=False)
    
    cities = Listing.objects.filter(
        city__icontains=q,
        is_available=True,
        is_approved=True
    ).only('city').values_list('city', flat=True).distinct()[:4]
    
    return JsonResponse(list(cities), safe=False)


def map_view(request):
    listings_json = cache.get("map_listings_json")

    if listings_json is None:
        listings = list(
            Listing.objects.filter(
                is_available=True,
                is_approved=True,
                latitude__isnull=False,
                longitude__isnull=False,
            )
            .exclude(status__in=["Vendu", "Loué"])
            .values(
                "title",
                "city",
                "price",
                "property_type",
                "status",
                "latitude",
                "longitude",
                "slug",
            )[:500]
        )

        listings_json = json.dumps(
            listings,
            cls=DjangoJSONEncoder
        )

        cache.set(
            "map_listings_json",
            listings_json,
            60 * 10  # 10 minutes
        )

    return render(
        request,
        "listings/map.html",
        {
            "listings_json": listings_json
        }
    )