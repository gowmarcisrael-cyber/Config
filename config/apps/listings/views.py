from django.shortcuts import render, redirect,get_object_or_404
from .models import Listing,Favorite
from django.http import HttpResponse
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
# Create your views here.

def home(request):
    listings = Listing.objects.all()[:6]
    context = {
        'listings':listings,
        'types':Listing.TYPES,
        'statuses':Listing.STATUS[:2],
        }
    return render(request,'listings/index.html',context=context)

def search(request):
    listings = Listing.objects.filter(is_available=True)

    status = request.GET.get('status')
    city = request.GET.get('city')
    property_type = request.GET.get('property_type')
    price_max = request.GET.get('price_max')

    if status:
        listings = listings.filter(status=status)
    if city:
        listings = listings.filter(city__icontains=city)
    if property_type:
        listings = listings.filter(property_type=property_type)
    if price_max:
        listings = listings.filter(price__lte=price_max)

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
            return redirect('listing-detail', id=listing.id)
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
    listing = get_object_or_404(Listing,pk=pk)
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

# Vue réservé au staff
@staff_member_required
def staff_listings(request):
    listings = Listing.objects.all().order_by('-created_at')

    # Filtres
    status = request.GET.get('status')
    is_approved = request.GET.get('is_approved')
    search = request.GET.get('search')

    if status:
        listings = listings.filter(status=status)
    if is_approved == '1':
        listings = listings.filter(is_approved=True)
    elif is_approved == '0':
        listings = listings.filter(is_approved=False)
    if search:
        listings = listings.filter(title__icontains=search)

    page = request.GET.get('page')
    listings = Paginator(listings, 10).get_page(page)

    context = {
        'listings': listings,
        'statuses': Listing.STATUS,
        'filters': request.GET,
    }
    return render(request, 'staff/listings.html', context=context)

@staff_member_required
@require_POST
def staff_approve_listing(request, pk):
    listing = get_object_or_404(Listing,pk=pk)
    listing.is_approved = not listing.is_approved
    listing.save()
    context = {
        'listing':listing
    }
    return render(request,'staff/partials/approve_listing.html',
                  context=context)

@staff_member_required
def staff_users(request):
    User = get_user_model()
    users = User.objects.exclude(is_staff=True).order_by('-date_joined')

    search = request.GET.get('search')
    if search:
        users = users.filter(username__icontains=search) | users.filter(email__icontains=search)

    page = request.GET.get('page')
    users = Paginator(users, 30).get_page(page)

    context = {
        'users': users,
        'filters': request.GET,
    }
    return render(request, 'staff/users.html', context=context)

@staff_member_required
@require_POST
def staff_toggle_user(request, pk):
    User = get_object_or_404(get_user_model(), pk=pk)
    User.is_active = not User.is_active
    User.save()
    context = {
        'user': User,
    }
    return render(request, 'staff/partials/toggle_user_btn.html', context=context)

from django.utils import timezone
from datetime import timedelta

@staff_member_required
def staff_stats(request):
    thirty_days_ago = timezone.now() - timedelta(days=30)

    listings_count = Listing.objects.count()
    approved_listings_count = Listing.objects.filter(is_approved=True).count()
    not_approved_listings_count = listings_count - approved_listings_count
    recent_listings_count = Listing.objects.filter(created_at__gte=thirty_days_ago).count()

    User = get_user_model()
    users_count = User.objects.count()
    active_users_count = User.objects.filter(is_active=True).count()
    not_active_users_count = users_count - active_users_count
    recent_users_count = User.objects.filter(date_joined__gte=thirty_days_ago).count()

    visits_count = Visit.objects.count()
    pending_visits_count = Visit.objects.filter(status='En attente').count()
    accepted_visits_count = Visit.objects.filter(status='Acceptée').count()

    repported_listing_count = Report.objects.count()
    resolved_reported_listing_count = Report.objects.filter(is_resolved=True).count()
    not_resolved_reported_listing_count = repported_listing_count - resolved_reported_listing_count 

    context = {
        'listings_count': listings_count,
        'approved_listings_count': approved_listings_count,
        'not_approved_listings_count': not_approved_listings_count,
        'recent_listings_count': recent_listings_count,
        'users_count': users_count,
        'active_users_count': active_users_count,
        'not_active_users_count': not_active_users_count,
        'recent_users_count': recent_users_count,
        'visits_count': visits_count,
        'pending_visits_count': pending_visits_count,
        'accepted_visits_count': accepted_visits_count,
        'reported_listing_count':repported_listing_count,
        'resolved_reported_listing_count':resolved_reported_listing_count,
        'not_resolved_reported_listing_count':not_resolved_reported_listing_count,
    }
    return render(request, 'staff/stats.html', context=context)

@staff_member_required
def staff_reports(request):
    reports = Report.objects.all().order_by('-created_at').select_related('author', 'listing', 'reported_user')

    is_resolved = request.GET.get('is_resolved')
    if is_resolved == '1':
        reports = reports.filter(is_resolved=True)
    elif is_resolved == '0':
        reports = reports.filter(is_resolved=False)

    page = request.GET.get('page')
    reports = Paginator(reports, 10).get_page(page)

    context = {
        'reports': reports,
        'filters': request.GET,
    }
    return render(request, 'staff/reports.html', context=context)

@staff_member_required
@require_POST
def resolve_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    report.is_resolved = not report.is_resolved
    report.save()
    return render(request, 'staff/partials/report_resolve_btn.html', {'report': report})