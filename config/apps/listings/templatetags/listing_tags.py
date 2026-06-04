from django import template

register = template.Library()

@register.simple_tag
def is_favorited(user, listing):
    if not user.is_authenticated:
        return False
    return listing.likes.filter(pk=user.pk).exists()