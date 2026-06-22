from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

@shared_task
def send_welcome_email_task(user_id, activation_link):
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    subject = "Bienvenue sur HAVEN"
    html_content = render_to_string(
        "emails/welcome.html",
        {"user": user, "activation_link": activation_link}
    )
    text_content = f"Activez votre compte ici : {activation_link}"

    email = EmailMultiAlternatives(
        subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

def send_delete_confirmation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    delete_link = request.build_absolute_uri(
        f"/accounts/delete/{uid}/{token}/"
    )
    subject = "Confirmer la suppression de votre compte — HAVEN"
    html_content = render_to_string(
        "emails/account_delete_confirmation.html",
        {
            "user": user,
            "delete_link": delete_link,
        }
    )
    text_content = f"Confirmer la suppression : {delete_link}"

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
