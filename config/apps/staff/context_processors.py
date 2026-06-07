from apps.listings.models import Listing
from apps.reports.models import Report

def staff_context(request):
    if request.user.is_authenticated and request.user.is_staff:
        return {
            'pending_listings_count': Listing.objects.filter(is_approved=False).count(),
            'pending_reports_count': Report.objects.filter(is_resolved=False).count(),
        }
    return {}