from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from celery import shared_task
from .models import Visit

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)
def send_visit_status_email(visit_id,listing_url):
    try:
        visit = Visit.objects.select_related(
            "sender",
            "receiver",
            "listing"
        ).get(id=visit_id)
    except Visit.DoesNotExist:
        return
    subject = f"Demande de visite {visit.status} — {visit.listing.title}"
    html_content = render_to_string(
        "emails/visit_status_update.html",
        {
            "sender": visit.sender.username,
            "receiver": visit.receiver.username,
            "listing": visit.listing,
            "date": visit.date,
            "message": visit.message,
            "status": visit.status,
            "listing_url": listing_url,
        }
    )
    text_content = f"Votre demande de visite pour {visit.listing.title} a été {visit.status}."

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [visit.sender.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)
def send_visit_request_email(visit_id,listing_url):
    try:
        visit = Visit.objects.get(id=visit_id)
    except Visit.DoesNotExist:
        
        return
    subject = f"Nouvelle demande de visite — {visit.listing.title}"
    html_content = render_to_string(
        "emails/visit_request.html",
        {
            "sender": visit.sender.username,
            "listing": visit.listing,
            "date": visit.date,
            "message": visit.message,
            "listing_url": listing_url
        }
    )
    text_content = f"Nouvelle demande de visite de {visit.sender.username} pour {visit.listing.title}"

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [visit.receiver.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
