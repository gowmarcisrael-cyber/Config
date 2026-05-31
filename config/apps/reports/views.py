from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from apps.listings.models import Listing
from .models import Report
from django.contrib.auth import get_user_model

# Create your views here.

User = get_user_model()

@login_required
@require_POST
def report_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if listing.user == request.user:
        return redirect('listing_detail', pk=pk)

    # Eviter les doublons
    if Report.objects.filter(author=request.user, listing=listing).exists():
        return redirect('listing_detail', id=pk)

    reason = request.POST.get('reason')
    message = request.POST.get('message', '')

    report = Report.objects.create(
        author=request.user,
        listing=listing,
        reason=reason,
        message=message,
    )
    return render(request, 'reports/report_done.html', {'report': report})


@login_required
@require_POST
def report_user(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)

    if user == request.user:
        return redirect('home')

    # Eviter les doublons
    if Report.objects.filter(author=request.user, reported_user=user).exists():
        return redirect('home')

    reason = request.POST.get('reason')
    message = request.POST.get('message', '')

    report = Report.objects.create(
        author=request.user,
        reported_user=user,
        reason=reason,
        message=message,
    )
    return render(request, 'reports/report_done.html', {'report': report})

@login_required
@require_POST
def delete_report(request, pk):
    report = get_object_or_404(Report, pk=pk, author=request.user)
    report.delete()
    return render(request, 'reports/report_deleted.html')