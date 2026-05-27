from django import template
from apps.listings.models import Favorite

register = template.Library()

@register.simple_tag
def is_favorited(user, listing):
    if not user.is_authenticated:
        return False
    return Favorite.objects.filter(user=user, listing=listing).exists()