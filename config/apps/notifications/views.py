from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Notification
# Create your views here.


def notify(user, notif_type, message, link=''):
    Notification.objects.create(
        user=user,
        notification_type=notif_type,
        message=message,
        link=link,
    )

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user)
    # Marquer toutes comme lues
    notifications.filter(is_read=False).update(is_read=True)
    context = {'notifications': notifications}
    if request.headers.get('HX-Request'):
        return render(request, 'notifications/list_fragment.html', context)
    return render(request, 'notifications/list.html',context=context)


@login_required
@require_POST
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications_list')