from .models import ViewedArticle
from django.utils import timezone
from datetime import timedelta


def fetch_viewed_articles(user, category, start_date, limit):
    return ViewedArticle.objects.filter(
        user=user,
        article__category=category,
        viewed_at__gte=start_date,
    ).order_by('-viewed_at')[:limit]
