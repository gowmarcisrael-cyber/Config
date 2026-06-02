from django.shortcuts import render
from apps.contacts.models import Message
from apps.listings.models import Listing
from apps.visits.models import Visit
from apps.reports.models import Report
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.utils import timezone
from datetime import timedelta
# Create your views here.

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
        listings = listings.annotate(
            rank=SearchRank(SearchVector('title',weight='A'),SearchQuery(search))
        ).filter(rank__gte=0.1).order_by('-rank')

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
        search_vector = SearchVector('username', weight='A') + SearchVector('email', weight='B')
        search_query = SearchQuery(search)
        users = users.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(rank__gte=0.1).order_by('-rank')

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

@staff_member_required
def staff_message(request):
    page = request.GET.get('page')
    messages = Paginator(Message.objects.order_by('-is_read'),8).get_page(page)
    context = {
        'contact_msgs':messages
    }
    return render(request,'staff/messages.html',context=context)

@require_POST
def toggle_message_read(request,pk):
    msg = get_object_or_404(Message,pk=pk)
    msg.is_read = not msg.is_read
    msg.save()
    context = {
        'msg':msg
    }
    return render(request,'staff/partials/read_btn.html',context=context)